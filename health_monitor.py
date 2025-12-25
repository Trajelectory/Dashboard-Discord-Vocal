
import time
from datetime import datetime
from threading import Lock

class HealthMonitor:
    """Monitore la santé de l'application"""
    
    def __init__(self):
        self.lock = Lock()
        self.bot_status = {
            'connected': False,
            'last_heartbeat': None,
            'last_update': None,
            'guild_count': 0,
            'error_count': 0,
            'last_error': None
        }
        self.web_status = {
            'connected_clients': 0,
            'last_request': None,
            'total_requests': 0
        }
        self.start_time = datetime.now()
    
    def bot_heartbeat(self):
        """Appelé régulièrement par le bot pour signaler qu'il est vivant"""
        with self.lock:
            self.bot_status['last_heartbeat'] = datetime.now()
            self.bot_status['connected'] = True
    
    def bot_update(self, guild_count):
        """Appelé quand le bot met à jour les données"""
        with self.lock:
            self.bot_status['last_update'] = datetime.now()
            self.bot_status['guild_count'] = guild_count
    
    def bot_error(self, error_msg):
        """Enregistre une erreur du bot"""
        with self.lock:
            self.bot_status['error_count'] += 1
            self.bot_status['last_error'] = {
                'message': str(error_msg),
                'timestamp': datetime.now()
            }
    
    def web_request(self):
        """Enregistre une requête web"""
        with self.lock:
            self.web_status['last_request'] = datetime.now()
            self.web_status['total_requests'] += 1
    
    def client_connected(self):
        """Incrémente le nombre de clients connectés"""
        with self.lock:
            self.web_status['connected_clients'] += 1
    
    def client_disconnected(self):
        """Décrémente le nombre de clients connectés"""
        with self.lock:
            self.web_status['connected_clients'] = max(0, self.web_status['connected_clients'] - 1)
    
    def get_status(self):
        """Retourne le statut complet de l'application"""
        with self.lock:
            now = datetime.now()
            
            bot_alive = False
            if self.bot_status['last_heartbeat']:
                time_since_heartbeat = (now - self.bot_status['last_heartbeat']).total_seconds()
                bot_alive = time_since_heartbeat < 30
            
            uptime = now - self.start_time
            
            return {
                'status': 'healthy' if bot_alive else 'degraded',
                'uptime_seconds': uptime.total_seconds(),
                'bot': {
                    'alive': bot_alive,
                    'connected': self.bot_status['connected'],
                    'last_heartbeat': self.bot_status['last_heartbeat'].isoformat() if self.bot_status['last_heartbeat'] else None,
                    'last_update': self.bot_status['last_update'].isoformat() if self.bot_status['last_update'] else None,
                    'guild_count': self.bot_status['guild_count'],
                    'error_count': self.bot_status['error_count'],
                    'last_error': self.bot_status['last_error']
                },
                'web': {
                    'connected_clients': self.web_status['connected_clients'],
                    'total_requests': self.web_status['total_requests'],
                    'last_request': self.web_status['last_request'].isoformat() if self.web_status['last_request'] else None
                },
                'timestamp': now.isoformat()
            }

# Instance globale
health_monitor = HealthMonitor()