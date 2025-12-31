# -*- coding: utf-8 -*-

from datetime import datetime
from threading import Lock
from collections import deque

class ActivityLogger:
    """Gère les logs d'activité vocale et toutes les actions"""
    
    def __init__(self, max_logs=100):
        self.lock = Lock()
        self.logs = deque(maxlen=max_logs)
        self.current_members = {}
        self.member_states = {}  # Pour tracker les états précédents
    
    def log_join(self, member_name, channel_name):
        """Enregistre une connexion"""
        with self.lock:
            log_entry = {
                'type': 'join',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            self.current_members[member_name] = channel_name
            return log_entry
    
    def log_leave(self, member_name, channel_name):
        """Enregistre une déconnexion"""
        with self.lock:
            log_entry = {
                'type': 'leave',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            if member_name in self.current_members:
                del self.current_members[member_name]
            if member_name in self.member_states:
                del self.member_states[member_name]
            return log_entry
    
    def log_move(self, member_name, from_channel, to_channel):
        """Enregistre un déplacement entre salons"""
        with self.lock:
            log_entry = {
                'type': 'move',
                'member': member_name,
                'from_channel': from_channel,
                'to_channel': to_channel,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            self.current_members[member_name] = to_channel
            return log_entry
    
    def log_mute(self, member_name, channel_name):
        """Enregistre quand quelqu'un se mute"""
        with self.lock:
            log_entry = {
                'type': 'mute',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_unmute(self, member_name, channel_name):
        """Enregistre quand quelqu'un se démute"""
        with self.lock:
            log_entry = {
                'type': 'unmute',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_deafen(self, member_name, channel_name):
        """Enregistre quand quelqu'un se met sourd"""
        with self.lock:
            log_entry = {
                'type': 'deafen',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_undeafen(self, member_name, channel_name):
        """Enregistre quand quelqu'un enlève la sourdine"""
        with self.lock:
            log_entry = {
                'type': 'undeafen',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_stream_start(self, member_name, channel_name):
        """Enregistre quand quelqu'un démarre un stream"""
        with self.lock:
            log_entry = {
                'type': 'stream_start',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_stream_stop(self, member_name, channel_name):
        """Enregistre quand quelqu'un arrête son stream"""
        with self.lock:
            log_entry = {
                'type': 'stream_stop',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_webcam_on(self, member_name, channel_name):
        """Enregistre quand quelqu'un active sa webcam"""
        with self.lock:
            log_entry = {
                'type': 'webcam_on',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_webcam_off(self, member_name, channel_name):
        """Enregistre quand quelqu'un désactive sa webcam"""
        with self.lock:
            log_entry = {
                'type': 'webcam_off',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_server_mute(self, member_name, channel_name):
        """Enregistre quand le serveur mute quelqu'un"""
        with self.lock:
            log_entry = {
                'type': 'server_mute',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def log_server_unmute(self, member_name, channel_name):
        """Enregistre quand le serveur unmute quelqu'un"""
        with self.lock:
            log_entry = {
                'type': 'server_unmute',
                'member': member_name,
                'channel': channel_name,
                'timestamp': datetime.now().isoformat(),
                'time_str': datetime.now().strftime('%H:%M:%S')
            }
            self.logs.append(log_entry)
            return log_entry
    
    def get_logs(self, limit=50):
        """Retourne les derniers logs"""
        with self.lock:
            return list(self.logs)[-limit:]
    
    def get_all_logs(self):
        """Retourne tous les logs"""
        with self.lock:
            return list(self.logs)
    
    def clear_logs(self):
        """Efface tous les logs"""
        with self.lock:
            self.logs.clear()

# Instance globale
activity_logger = ActivityLogger(max_logs=200)
