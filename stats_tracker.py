# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from threading import Lock
from collections import defaultdict
import sqlite3
import json
from config import DATABASE_PATH

class StatsTracker:
    """Suit les statistiques d'utilisation des vocaux avec persistance SQLite"""
    
    def __init__(self, db_path=None):
        self.lock = Lock()
        self.db_path = db_path or DATABASE_PATH
        
        # Sessions actives en mémoire
        self.active_sessions = {}
        
        # Initialiser la base de données
        self._init_database()
        
        # Charger les sessions actives depuis la DB (en cas de crash)
        self._load_active_sessions()
    
    def _init_database(self):
        """Crée les tables si elles n'existent pas"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des sessions complètes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL,
                    channels TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des records
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_type TEXT NOT NULL UNIQUE,
                    member_name TEXT,
                    duration REAL,
                    date TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialiser les records s'ils n'existent pas
            record_types = ['longest_session_today', 'longest_session_week', 
                          'longest_session_month', 'longest_session_ever']
            for record_type in record_types:
                cursor.execute('''
                    INSERT OR IGNORE INTO records (record_type, member_name, duration, date)
                    VALUES (?, NULL, 0, NULL)
                ''', (record_type,))
            
            # Index pour améliorer les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_name ON sessions(member_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_time ON sessions(start_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_active ON sessions(is_active)')
            
            conn.commit()
            conn.close()
    
    def _load_active_sessions(self):
        """Charge les sessions actives depuis la DB (récupération après crash)"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT member_name, start_time, channels
                FROM sessions
                WHERE is_active = 1 AND end_time IS NULL
            ''')
            
            for row in cursor.fetchall():
                member_name, start_time, channels_json = row
                channels = json.loads(channels_json) if channels_json else []
                
                self.active_sessions[member_name] = {
                    'channel': channels[-1] if channels else 'Unknown',
                    'join_time': datetime.fromisoformat(start_time),
                    'channel_changes': []
                }
            
            conn.close()
            
            if self.active_sessions:
                print(f"📊 {len(self.active_sessions)} sessions actives récupérées")
    
    def member_joined(self, member_name, channel_name):
        """Enregistre qu'un membre a rejoint un vocal"""
        with self.lock:
            now = datetime.now()
            
            # Mémoire
            self.active_sessions[member_name] = {
                'channel': channel_name,
                'join_time': now,
                'channel_changes': []
            }
            
            # Base de données
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (member_name, start_time, channels, is_active)
                VALUES (?, ?, ?, 1)
            ''', (member_name, now.isoformat(), json.dumps([channel_name])))
            
            conn.commit()
            conn.close()
    
    def member_left(self, member_name):
        """Enregistre qu'un membre a quitté le vocal"""
        with self.lock:
            if member_name not in self.active_sessions:
                return
            
            session = self.active_sessions[member_name]
            now = datetime.now()
            duration = (now - session['join_time']).total_seconds()
            
            channels = [session['channel']] + [ch['to'] for ch in session['channel_changes']]
            
            # Mettre à jour la base de données
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, duration = ?, channels = ?, is_active = 0
                WHERE member_name = ? AND is_active = 1 AND end_time IS NULL
            ''', (now.isoformat(), duration, json.dumps(channels), member_name))
            
            conn.commit()
            conn.close()
            
            # Vérifier les records
            self._check_records(member_name, duration, session['join_time'])
            
            # Nettoyer la mémoire
            del self.active_sessions[member_name]
    
    def member_moved(self, member_name, from_channel, to_channel):
        """Enregistre qu'un membre a changé de canal"""
        with self.lock:
            if member_name in self.active_sessions:
                self.active_sessions[member_name]['channel_changes'].append({
                    'from': from_channel,
                    'to': to_channel,
                    'time': datetime.now().isoformat()
                })
                self.active_sessions[member_name]['channel'] = to_channel
    
    def _check_records(self, member_name, duration, join_time):
        """Vérifie et met à jour les records"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record du jour
        if join_time.date() == now.date():
            cursor.execute('''
                SELECT duration FROM records WHERE record_type = 'longest_session_today'
            ''')
            current = cursor.fetchone()[0]
            if duration > current:
                cursor.execute('''
                    UPDATE records
                    SET member_name = ?, duration = ?, date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE record_type = 'longest_session_today'
                ''', (member_name, duration, join_time.isoformat()))
        
        # Record de la semaine
        week_start = now - timedelta(days=now.weekday())
        if join_time.date() >= week_start.date():
            cursor.execute('''
                SELECT duration FROM records WHERE record_type = 'longest_session_week'
            ''')
            current = cursor.fetchone()[0]
            if duration > current:
                cursor.execute('''
                    UPDATE records
                    SET member_name = ?, duration = ?, date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE record_type = 'longest_session_week'
                ''', (member_name, duration, join_time.isoformat()))
        
        # Record du mois
        if join_time.month == now.month and join_time.year == now.year:
            cursor.execute('''
                SELECT duration FROM records WHERE record_type = 'longest_session_month'
            ''')
            current = cursor.fetchone()[0]
            if duration > current:
                cursor.execute('''
                    UPDATE records
                    SET member_name = ?, duration = ?, date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE record_type = 'longest_session_month'
                ''', (member_name, duration, join_time.isoformat()))
        
        # Record all-time
        cursor.execute('''
            SELECT duration FROM records WHERE record_type = 'longest_session_ever'
        ''')
        current = cursor.fetchone()[0]
        if duration > current:
            cursor.execute('''
                UPDATE records
                SET member_name = ?, duration = ?, date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE record_type = 'longest_session_ever'
            ''', (member_name, duration, join_time.isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_current_sessions(self):
        """Retourne les sessions en cours avec leur durée actuelle"""
        with self.lock:
            now = datetime.now()
            current = {}
            for member_name, session in self.active_sessions.items():
                duration = (now - session['join_time']).total_seconds()
                current[member_name] = {
                    'channel': session['channel'],
                    'duration': duration,
                    'join_time': session['join_time'].isoformat()
                }
            return current
    
    def get_daily_stats(self, member_name=None):
        """Retourne les stats du jour"""
        with self.lock:
            today = datetime.now().date().isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if member_name:
                cursor.execute('''
                    SELECT SUM(duration), COUNT(*), channels
                    FROM sessions
                    WHERE member_name = ? AND DATE(start_time) = ? AND is_active = 0
                ''', (member_name, today))
            else:
                cursor.execute('''
                    SELECT member_name, SUM(duration), COUNT(*), GROUP_CONCAT(channels)
                    FROM sessions
                    WHERE DATE(start_time) = ? AND is_active = 0
                    GROUP BY member_name
                ''', (today,))
            
            results = {}
            for row in cursor.fetchall():
                if member_name:
                    total_time, session_count, channels_json = row
                    name = member_name
                else:
                    name, total_time, session_count, channels_json = row
                
                # Extraire les canaux uniques
                channels_visited = set()
                if channels_json:
                    for ch_list in channels_json.split(','):
                        try:
                            channels_visited.update(json.loads(ch_list))
                        except:
                            pass
                
                # Ajouter le temps de la session en cours si elle existe
                current_duration = 0
                if name in self.active_sessions:
                    now = datetime.now()
                    current_duration = (now - self.active_sessions[name]['join_time']).total_seconds()
                    total_time = (total_time or 0) + current_duration
                    session_count = (session_count or 0) + 1
                    channels_visited.add(self.active_sessions[name]['channel'])
                
                results[name] = {
                    'total_time': total_time or 0,
                    'session_count': session_count or 0,
                    'average_session': (total_time / session_count) if session_count and total_time else 0,
                    'channels_visited': list(channels_visited)
                }
            
            conn.close()
            return results if not member_name else results.get(member_name, self._empty_stats())
    
    def get_weekly_stats(self, member_name=None):
        """Retourne les stats de la semaine"""
        with self.lock:
            now = datetime.now()
            week_start = (now - timedelta(days=now.weekday())).date().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if member_name:
                cursor.execute('''
                    SELECT SUM(duration), COUNT(*), channels
                    FROM sessions
                    WHERE member_name = ? AND DATE(start_time) >= ? AND is_active = 0
                ''', (member_name, week_start))
            else:
                cursor.execute('''
                    SELECT member_name, SUM(duration), COUNT(*), GROUP_CONCAT(channels)
                    FROM sessions
                    WHERE DATE(start_time) >= ? AND is_active = 0
                    GROUP BY member_name
                ''', (week_start,))
            
            results = {}
            for row in cursor.fetchall():
                if member_name:
                    total_time, session_count, channels_json = row
                    name = member_name
                else:
                    name, total_time, session_count, channels_json = row
                
                channels_visited = set()
                if channels_json:
                    for ch_list in channels_json.split(','):
                        try:
                            channels_visited.update(json.loads(ch_list))
                        except:
                            pass
                
                results[name] = {
                    'total_time': total_time or 0,
                    'session_count': session_count or 0,
                    'average_session': (total_time / session_count) if session_count and total_time else 0,
                    'channels_visited': list(channels_visited)
                }
            
            conn.close()
            return results if not member_name else results.get(member_name, self._empty_stats())
    
    def _empty_stats(self):
        """Retourne des stats vides"""
        return {
            'total_time': 0,
            'session_count': 0,
            'average_session': 0,
            'channels_visited': []
        }
    
    def get_top_users_today(self, limit=10):
        """Retourne le top des utilisateurs du jour"""
        with self.lock:
            today = datetime.now().date().isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT member_name, SUM(duration) as total
                FROM sessions
                WHERE DATE(start_time) = ? AND is_active = 0
                GROUP BY member_name
                ORDER BY total DESC
                LIMIT ?
            ''', (today, limit))
            
            results = []
            for row in cursor.fetchall():
                member_name, total_time = row
                
                # Ajouter le temps de la session en cours
                if member_name in self.active_sessions:
                    now = datetime.now()
                    current_duration = (now - self.active_sessions[member_name]['join_time']).total_seconds()
                    total_time += current_duration
                
                results.append({
                    'member': member_name,
                    'total_time': total_time
                })
            
            # Ajouter les membres qui n'ont qu'une session en cours
            for member_name, session in self.active_sessions.items():
                if not any(r['member'] == member_name for r in results):
                    now = datetime.now()
                    duration = (now - session['join_time']).total_seconds()
                    results.append({
                        'member': member_name,
                        'total_time': duration
                    })
            
            # Re-trier et limiter
            results.sort(key=lambda x: x['total_time'], reverse=True)
            
            conn.close()
            return results[:limit]
    
    def get_records(self):
        """Retourne tous les records"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT record_type, member_name, duration, date FROM records')
            
            records = {}
            for row in cursor.fetchall():
                record_type, member_name, duration, date = row
                records[record_type] = {
                    'member': member_name,
                    'duration': duration,
                    'date': date
                }
            
            conn.close()
            return records
    
    def reset_daily_stats(self):
        """Réinitialise les stats quotidiennes"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE records
                SET member_name = NULL, duration = 0, date = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE record_type = 'longest_session_today'
            ''')
            
            conn.commit()
            conn.close()
    
    def reset_weekly_stats(self):
        """Réinitialise les stats hebdomadaires"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE records
                SET member_name = NULL, duration = 0, date = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE record_type = 'longest_session_week'
            ''')
            
            conn.commit()
            conn.close()
    
    def reset_monthly_stats(self):
        """Réinitialise les stats mensuelles"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE records
                SET member_name = NULL, duration = 0, date = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE record_type = 'longest_session_month'
            ''')
            
            conn.commit()
            conn.close()

# Instance globale
stats_tracker = StatsTracker()