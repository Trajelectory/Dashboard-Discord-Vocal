# -*- coding: utf-8 -*-
import discord
import asyncio
import copy
from discord.ext import commands, tasks
from config import DISCORD_TOKEN, VOICE_CHANNEL_IDS, TEST_MODE
from test_data import get_test_data
from health_monitor import health_monitor
from activity_logger import activity_logger
from stats_tracker import stats_tracker

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
    """Compare l'état actuel avec l'état précédent et log tous les changements"""
    global previous_voice_data, voice_data
    
    # Crée un set des membres actuels par salon
    current_state = {}
    for channel_name, data in voice_data.items():
        current_state[channel_name] = {}
        for m in data['members']:
            current_state[channel_name][m['name']] = {
                'muted': m.get('muted', False),
                'deafened': m.get('deafened', False),
                'server_muted': m.get('server_muted', False),
                'server_deafened': m.get('server_deafened', False),
                'stream': m.get('stream', False),
                'webcam': m.get('webcam', False)
            }
    
    # Crée un set des membres précédents par salon
    previous_state = {}
    for channel_name, data in previous_voice_data.items():
        previous_state[channel_name] = {}
        for m in data['members']:
            previous_state[channel_name][m['name']] = {
                'muted': m.get('muted', False),
                'deafened': m.get('deafened', False),
                'server_muted': m.get('server_muted', False),
                'server_deafened': m.get('server_deafened', False),
                'stream': m.get('stream', False),
                'webcam': m.get('webcam', False)
            }
    
    # Détecte les changements
    all_channels = set(current_state.keys()) | set(previous_state.keys())
    
    for channel_name in all_channels:
        current_members = set(current_state.get(channel_name, {}).keys())
        previous_members = set(previous_state.get(channel_name, {}).keys())
        
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
                stats_tracker.member_moved(member, came_from, channel_name)  # ← AJOUT
            else:
                log = activity_logger.log_join(member, channel_name)
                stats_tracker.member_joined(member, channel_name)  # ← AJOUT
            
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
                stats_tracker.member_left(member)  # ← AJOUT
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
        
        # Membres qui sont restés dans le même salon - vérifier les changements d'état
        staying = current_members & previous_members
        for member in staying:
            prev = previous_state[channel_name][member]
            curr = current_state[channel_name][member]
            
            # Mute/Unmute
            if not prev['muted'] and curr['muted']:
                log = activity_logger.log_mute(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            elif prev['muted'] and not curr['muted']:
                log = activity_logger.log_unmute(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            
            # Deafen/Undeafen
            if not prev['deafened'] and curr['deafened']:
                log = activity_logger.log_deafen(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            elif prev['deafened'] and not curr['deafened']:
                log = activity_logger.log_undeafen(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            
            # Server Mute/Unmute
            if not prev['server_muted'] and curr['server_muted']:
                log = activity_logger.log_server_mute(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            elif prev['server_muted'] and not curr['server_muted']:
                log = activity_logger.log_server_unmute(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            
            # Stream Start/Stop
            if not prev['stream'] and curr['stream']:
                log = activity_logger.log_stream_start(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            elif prev['stream'] and not curr['stream']:
                log = activity_logger.log_stream_stop(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            
            # Webcam On/Off
            if not prev['webcam'] and curr['webcam']:
                log = activity_logger.log_webcam_on(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
            elif prev['webcam'] and not curr['webcam']:
                log = activity_logger.log_webcam_off(member, channel_name)
                if socketio_instance:
                    socketio_instance.emit('activity_log', log)
    
    # Sauvegarde l'état actuel pour la prochaine comparaison
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

def get_member_full_info(member_name):
    """
    Récupère les informations complètes d'un membre
    
    Args:
        member_name: Nom du membre à rechercher
        
    Returns:
        dict avec toutes les infos du membre ou None si non trouvé
    """
    for guild in bot.guilds:
        for channel_id in VOICE_CHANNEL_IDS:
            channel = guild.get_channel(channel_id)
            if channel and isinstance(channel, discord.VoiceChannel):
                for member in channel.members:
                    if member.display_name.lower() == member_name.lower() or member.name.lower() == member_name.lower():
                        # Informations de base
                        voice_state = member.voice
                        
                        # Informations du profil
                        member_info = {
                            # Identité
                            'id': str(member.id),
                            'username': member.name,
                            'discriminator': member.discriminator,
                            'display_name': member.display_name,
                            'nick': member.nick,
                            'mention': member.mention,
                            
                            # Avatars et bannière
                            'avatar_url': str(member.display_avatar.url),
                            'avatar_url_static': str(member.display_avatar.with_static_format('png').url),
                            'default_avatar_url': str(member.default_avatar.url),
                            'guild_avatar_url': str(member.guild_avatar.url) if member.guild_avatar else None,
                            
                            # Statut et activité
                            'status': str(member.status),
                            'raw_status': str(member.raw_status),
                            'mobile_status': str(member.mobile_status),
                            'desktop_status': str(member.desktop_status),
                            'web_status': str(member.web_status),
                            
                            # Activités en cours
                            'activities': [],
                            'custom_activity': None,
                            'spotify': None,
                            
                            # État vocal
                            'voice': {
                                'channel': channel.name,
                                'channel_id': str(channel.id),
                                'muted': voice_state.self_mute if voice_state else False,
                                'deafened': voice_state.self_deaf if voice_state else False,
                                'server_muted': voice_state.mute if voice_state else False,
                                'server_deafened': voice_state.deaf if voice_state else False,
                                'streaming': voice_state.self_stream if voice_state else False,
                                'video': voice_state.self_video if voice_state else False,
                                'suppress': voice_state.suppress if voice_state else False,
                                'requested_to_speak_at': voice_state.requested_to_speak_at.isoformat() if voice_state and voice_state.requested_to_speak_at else None
                            },
                            
                            # Rôles
                            'roles': [
                                {
                                    'id': str(role.id),
                                    'name': role.name,
                                    'color': str(role.color),
                                    'position': role.position,
                                    'hoist': role.hoist,
                                    'mentionable': role.mentionable
                                }
                                for role in member.roles if role.name != "@everyone"
                            ],
                            'top_role': {
                                'name': member.top_role.name,
                                'color': str(member.top_role.color),
                                'position': member.top_role.position
                            },
                            'color': str(member.color),
                            
                            # Dates importantes
                            'created_at': member.created_at.isoformat(),
                            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                            'premium_since': member.premium_since.isoformat() if member.premium_since else None,
                            
                            # Badges et flags
                            'public_flags': [flag.name for flag in member.public_flags.all()],
                            'is_bot': member.bot,
                            'is_system': member.system,
                            
                            # Permissions
                            'guild_permissions': {
                                'administrator': member.guild_permissions.administrator,
                                'manage_guild': member.guild_permissions.manage_guild,
                                'manage_roles': member.guild_permissions.manage_roles,
                                'manage_channels': member.guild_permissions.manage_channels,
                                'kick_members': member.guild_permissions.kick_members,
                                'ban_members': member.guild_permissions.ban_members,
                                'manage_messages': member.guild_permissions.manage_messages,
                                'mention_everyone': member.guild_permissions.mention_everyone,
                                'view_audit_log': member.guild_permissions.view_audit_log,
                            },
                            
                            # Serveur
                            'guild': {
                                'id': str(guild.id),
                                'name': guild.name,
                                'icon_url': str(guild.icon.url) if guild.icon else None
                            }
                        }
                        
                        # Activités détaillées
                        for activity in member.activities:
                            if isinstance(activity, discord.Spotify):
                                member_info['spotify'] = {
                                    'title': activity.title,
                                    'artist': activity.artist,
                                    'album': activity.album,
                                    'album_cover_url': activity.album_cover_url,
                                    'track_url': activity.track_url,
                                    'duration': activity.duration.total_seconds() if activity.duration else None,
                                    'start': activity.start.isoformat() if activity.start else None,
                                    'end': activity.end.isoformat() if activity.end else None
                                }
                            elif isinstance(activity, discord.CustomActivity):
                                member_info['custom_activity'] = {
                                    'name': activity.name,
                                    'emoji': str(activity.emoji) if activity.emoji else None,
                                    'state': activity.state
                                }
                            elif isinstance(activity, discord.Game):
                                member_info['activities'].append({
                                    'type': 'game',
                                    'name': activity.name,
                                    'details': getattr(activity, 'details', None),
                                    'state': getattr(activity, 'state', None)
                                })
                            elif isinstance(activity, discord.Streaming):
                                member_info['activities'].append({
                                    'type': 'streaming',
                                    'name': activity.name,
                                    'url': activity.url,
                                    'details': getattr(activity, 'details', None),
                                    'platform': activity.platform if hasattr(activity, 'platform') else None
                                })
                            else:
                                member_info['activities'].append({
                                    'type': str(activity.type).split('.')[-1].lower(),
                                    'name': activity.name
                                })
                        
                        return member_info
    
    return None

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