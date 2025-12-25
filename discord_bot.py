# -*- coding: utf-8 -*-
import discord
import asyncio
import copy
from discord.ext import commands, tasks
from config import DISCORD_TOKEN, VOICE_CHANNEL_IDS, TEST_MODE
from test_data import get_test_data
from health_monitor import health_monitor
from activity_logger import activity_logger

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_data = {}
previous_voice_data = {}

socketio_instance = None

def set_socketio(socketio):
    global socketio_instance
    socketio_instance = socketio

def broadcast_update():
    """Envoie les données mises à jour à tous les clients connectés"""
    if socketio_instance:
        try:
            socketio_instance.emit('voice_update', voice_data)
            health_monitor.bot_heartbeat()
        except Exception as e:
            health_monitor.bot_error(f"Broadcast error: {e}")
            print(f"❌ Erreur broadcast: {e}")

def track_voice_changes():
    """Compare l'état actuel avec l'état précédent et log les changements"""
    global previous_voice_data, voice_data
    
    # Crée un set des membres actuels par salon
    current_state = {}
    for channel_name, data in voice_data.items():
        current_state[channel_name] = set(m['name'] for m in data['members'])
    
    # Crée un set des membres précédents par salon
    previous_state = {}
    for channel_name, data in previous_voice_data.items():
        previous_state[channel_name] = set(m['name'] for m in data['members'])
    
    # Détecte les changements
    all_channels = set(current_state.keys()) | set(previous_state.keys())
    
    for channel_name in all_channels:
        current_members = current_state.get(channel_name, set())
        previous_members = previous_state.get(channel_name, set())
        
        # Nouveaux membres (rejoints)
        joined = current_members - previous_members
        for member in joined:
            # Vérifie s'il vient d'un autre salon (move)
            came_from = None
            for other_channel, other_members in previous_state.items():
                if member in other_members and other_channel != channel_name:
                    came_from = other_channel
                    break
            
            if came_from:
                log = activity_logger.log_move(member, came_from, channel_name)
            else:
                log = activity_logger.log_join(member, channel_name)
            
            # Broadcast le log aux clients
            if socketio_instance:
                socketio_instance.emit('activity_log', log)
        
        # Membres partis
        left = previous_members - current_members
        for member in left:
            # Vérifie s'il est allé dans un autre salon
            went_to = None
            for other_channel, other_members in current_state.items():
                if member in other_members and other_channel != channel_name:
                    went_to = other_channel
                    break
            
            # Si pas de déplacement, c'est une vraie déconnexion
            if not went_to:
                log = activity_logger.log_leave(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
    
    # Sauvegarde l'état actuel pour la prochaine comparaison (copie profonde)
    previous_voice_data = copy.deepcopy(voice_data)

def update_voice_data():
    """Met à jour les données des salons vocaux"""
    global voice_data
    voice_data = {}
    
    try:
        if TEST_MODE:
            voice_data = get_test_data()
            health_monitor.bot_update(1)
            track_voice_changes()
            return
        
        guild_count = 0
        for guild in bot.guilds:
            guild_count += 1
            for channel_id in VOICE_CHANNEL_IDS:
                channel = guild.get_channel(channel_id)
                if channel and isinstance(channel, discord.VoiceChannel):
                    members = []
                    for m in channel.members:
                        voice_state = m.voice
                        members.append({
                            "name": m.display_name,
                            "avatar": str(m.display_avatar.url),
                            "status": str(m.status),
                            "webcam": voice_state.self_video if voice_state else False,
                            "stream": voice_state.self_stream if voice_state else False,
                            "muted": voice_state.self_mute if voice_state else False,
                            "deafened": voice_state.self_deaf if voice_state else False,
                            "server_muted": voice_state.mute if voice_state else False,
                            "server_deafened": voice_state.deaf if voice_state else False
                        })
                    voice_data[channel.name] = {
                        "members": members,
                        "count": len(members)
                    }
        
        health_monitor.bot_update(guild_count)
        track_voice_changes()
        
    except Exception as e:
        health_monitor.bot_error(f"Update error: {e}")
        print(f"❌ Erreur mise à jour: {e}")

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    health_monitor.bot_heartbeat()
    update_voice_data()
    broadcast_update()
    
    if not heartbeat_task.is_running():
        heartbeat_task.start()

@bot.event
async def on_voice_state_update(member, before, after):
    """Mise à jour automatique lors des changements vocaux"""
    update_voice_data()
    broadcast_update()

@tasks.loop(seconds=10)
async def heartbeat_task():
    """Envoie un heartbeat toutes les 10 secondes"""
    health_monitor.bot_heartbeat()
    
    if socketio_instance:
        try:
            status = health_monitor.get_status()
            socketio_instance.emit('health_status', status)
        except Exception as e:
            print(f"❌ Erreur envoi health status: {e}")

@bot.event
async def on_presence_update(before, after):
    """Mise à jour automatique lors des changements de statut"""
    if after.voice and after.voice.channel:
        if after.voice.channel.id in VOICE_CHANNEL_IDS:
            update_voice_data()
            broadcast_update()

@bot.event
async def on_error(event, *args, **kwargs):
    """Capture les erreurs Discord"""
    import traceback
    error_msg = traceback.format_exc()
    health_monitor.bot_error(error_msg)
    print(f"❌ Erreur Discord: {error_msg}")

def get_voice_data():
    return voice_data

def run_bot():
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        health_monitor.bot_error(f"Bot crash: {e}")
        print(f"❌ Bot crashed: {e}")