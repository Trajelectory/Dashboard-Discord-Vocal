# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from config import FLASK_HOST, FLASK_PORT, SECRET_KEY
from health_monitor import health_monitor
from activity_logger import activity_logger
import discord_bot

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

discord_bot.set_socketio(socketio)

@app.route('/')
def index():
    health_monitor.web_request()
    return render_template('index.html')  # Plus besoin de template.py !

@app.route('/health')
def health_check():
    health_monitor.web_request()
    status = health_monitor.get_status()
    http_code = 200 if status['status'] == 'healthy' else 503
    return jsonify(status), http_code

@app.route('/api/status')
def api_status():
    health_monitor.web_request()
    return jsonify(health_monitor.get_status())

@app.route('/api/logs')
def api_logs():
    health_monitor.web_request()
    logs = activity_logger.get_all_logs()
    return jsonify({'logs': logs})

@socketio.on('connect')
def handle_connect():
    print("🔌 Client connecté")
    health_monitor.client_connected()
    emit('voice_update', discord_bot.get_voice_data())
    emit('health_status', health_monitor.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 Client déconnecté")
    health_monitor.client_disconnected()

@socketio.on('ping')
def handle_ping():
    emit('pong', {'timestamp': health_monitor.get_status()['timestamp']})

@socketio.on('get_logs')
def handle_get_logs(data):
    limit = data.get('limit', 50) if data else 50
    logs = activity_logger.get_logs(limit)
    emit('logs_history', {'logs': logs})

def run_server():
    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=False, allow_unsafe_werkzeug=True)
