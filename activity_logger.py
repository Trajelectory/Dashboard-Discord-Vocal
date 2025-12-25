# -*- coding: utf-8 -*-

from datetime import datetime
from threading import Lock
from collections import deque

class ActivityLogger:
    """Gère les logs d'activité vocale"""
    
    def __init__(self, max_logs=100):
        self.lock = Lock()
        self.logs = deque(maxlen=max_logs)
        self.current_members = {}
    
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