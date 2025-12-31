# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from config import FLASK_HOST, FLASK_PORT, SECRET_KEY
from health_monitor import health_monitor
from activity_logger import activity_logger
import discord_bot
from stats_tracker import stats_tracker
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

discord_bot.set_socketio(socketio)

# ============================================
# ROUTES WEB
# ============================================

@app.route('/')
def index():
    """Interface web principale"""
    health_monitor.web_request()
    return render_template('index.html')

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api')
def api_documentation():
    """Page de documentation de l'API"""
    return render_template('api.html', base_url=request.url_root.rstrip('/'))

@app.route('/stats')
def stats_page():
    """Page de statistiques"""
    health_monitor.web_request()
    return render_template('stats.html')

@app.route('/api/bot')
def api_bot():
    """Retourne les données brutes du bot"""
    health_monitor.web_request()
    voice_data = discord_bot.get_voice_data()
    
    return jsonify({
        'success': True,
        'data': voice_data,
        'metadata': {
            'total_channels': len(voice_data),
            'total_members': sum(channel['count'] for channel in voice_data.values()),
            'timestamp': health_monitor.get_status()['timestamp']
        }
    })

@app.route('/api/bot/channels')
def api_bot_channels():
    """Liste des salons vocaux surveillés"""
    health_monitor.web_request()
    voice_data = discord_bot.get_voice_data()
    
    channels = []
    for channel_name, data in voice_data.items():
        channels.append({
            'name': channel_name,
            'member_count': data['count'],
            'members': [m['name'] for m in data['members']]
        })
    
    return jsonify({
        'success': True,
        'channels': channels,
        'total': len(channels)
    })

@app.route('/api/bot/members')
def api_bot_members():
    """Liste de tous les membres en vocal"""
    health_monitor.web_request()
    voice_data = discord_bot.get_voice_data()
    
    channel_filter = request.args.get('channel')
    
    all_members = []
    for channel_name, data in voice_data.items():
        if channel_filter and channel_name != channel_filter:
            continue
            
        for member in data['members']:
            member_info = member.copy()
            member_info['channel'] = channel_name
            all_members.append(member_info)
    
    return jsonify({
        'success': True,
        'members': all_members,
        'total': len(all_members),
        'filter': channel_filter
    })

@app.route('/api/bot/member/<member_name>')
def api_bot_member(member_name):
    """
    Informations détaillées sur un membre spécifique (profil complet)
    
    Args:
        member_name: Nom du membre (pseudo Discord ou display name)
    
    Returns:
        JSON avec toutes les infos du profil ou 404 si non trouvé
    """
    health_monitor.web_request()
    
    member_info = discord_bot.get_member_full_info(member_name)
    
    if member_info:
        return jsonify({
            'success': True,
            'member': member_info
        })
    
    return jsonify({
        'success': False,
        'error': 'Member not found in any voice channel',
        'member_name': member_name
    }), 404


@app.route('/api/bot/stats')
def api_bot_stats():
    """Statistiques générales des salons vocaux"""
    health_monitor.web_request()
    voice_data = discord_bot.get_voice_data()
    
    total_members = 0
    streaming_count = 0
    webcam_count = 0
    muted_count = 0
    deafened_count = 0
    
    status_count = {
        'online': 0,
        'idle': 0,
        'dnd': 0,
        'offline': 0
    }
    
    for channel_name, data in voice_data.items():
        total_members += data['count']
        for member in data['members']:
            if member.get('stream'):
                streaming_count += 1
            if member.get('webcam'):
                webcam_count += 1
            if member.get('muted') or member.get('server_muted'):
                muted_count += 1
            if member.get('deafened') or member.get('server_deafened'):
                deafened_count += 1
            
            status = member.get('status', 'offline')
            if status in status_count:
                status_count[status] += 1
    
    return jsonify({
        'success': True,
        'stats': {
            'total_channels': len(voice_data),
            'total_members': total_members,
            'streaming': streaming_count,
            'webcam_active': webcam_count,
            'muted': muted_count,
            'deafened': deafened_count,
            'status_breakdown': status_count
        }
    })

@app.route('/api/status')
def api_status():
    """Statut détaillé du système"""
    health_monitor.web_request()
    return jsonify(health_monitor.get_status())

@app.route('/api/logs')
def api_logs():
    """Historique des logs d'activité"""
    health_monitor.web_request()
    
    all_logs = activity_logger.get_all_logs()
    
    log_type = request.args.get('type')
    if log_type:
        all_logs = [log for log in all_logs if log['type'] == log_type]
    
    limit = request.args.get('limit', type=int)
    if limit:
        all_logs = all_logs[-limit:]
    
    return jsonify({
        'success': True,
        'logs': all_logs,
        'total': len(all_logs),
        'filters': {
            'type': log_type,
            'limit': limit
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_monitor.web_request()
    status = health_monitor.get_status()
    http_code = 200 if status['status'] == 'healthy' else 503
    return jsonify(status), http_code

# ============================================
# WEBSOCKET HANDLERS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Envoie les données initiales lors de la connexion"""
    print("🔌 Client connecté")
    health_monitor.client_connected()
    emit('voice_update', discord_bot.get_voice_data())
    emit('health_status', health_monitor.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion d'un client"""
    print("🔌 Client déconnecté")
    health_monitor.client_disconnected()

@socketio.on('ping')
def handle_ping():
    """Répond au ping du client"""
    emit('pong', {'timestamp': health_monitor.get_status()['timestamp']})

@socketio.on('get_logs')
def handle_get_logs(data):
    """Envoie les logs existants au client"""
    limit = data.get('limit', 50) if data else 50
    logs = activity_logger.get_logs(limit)
    emit('logs_history', {'logs': logs})

@socketio.on('get_stats')
def handle_get_stats(data):
    """Envoie les statistiques complètes"""
    period = data.get('period', 'today') if data else 'today'
    
    if period == 'today':
        all_stats = stats_tracker.get_daily_stats()
    else:
        all_stats = stats_tracker.get_weekly_stats()
    
    top_users = stats_tracker.get_top_users_today(limit=10)
    records = stats_tracker.get_records()
    current_sessions = stats_tracker.get_current_sessions()
    
    emit('stats_update', {
        'all_stats': all_stats,
        'top_users': top_users,
        'records': records,
        'current_sessions': current_sessions,
        'period': period
    })

# Mise à jour automatique des stats
def emit_stats_update():
    while True:
        time.sleep(30)
        try:
            all_stats = stats_tracker.get_daily_stats()
            top_users = stats_tracker.get_top_users_today(limit=10)
            records = stats_tracker.get_records()
            current_sessions = stats_tracker.get_current_sessions()
            
            socketio.emit('stats_update', {
                'all_stats': all_stats,
                'top_users': top_users,
                'records': records,
                'current_sessions': current_sessions,
                'period': 'today'
            })
        except Exception as e:
            print(f"❌ Erreur stats update: {e}")

# Démarrer le thread de mise à jour des stats
stats_thread = threading.Thread(target=emit_stats_update, daemon=True)
stats_thread.start()

# ============================================
# LANCEMENT DU SERVEUR
# ============================================

def run_server():
    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=False, allow_unsafe_werkzeug=True)