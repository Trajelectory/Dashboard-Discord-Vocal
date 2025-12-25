# -*- coding: utf-8 -*-

def get_test_data():
    """Retourne des données de test pour le mode démo"""
    return {
        "🎧 Salon Principal": {
            "members": [
                {
                    "name": "Alice",
                    "avatar": "https://i.pravatar.cc/150?img=1",
                    "status": "online",
                    "webcam": True,
                    "stream": False,
                    "muted": False,
                    "deafened": False,
                    "server_muted": False,
                    "server_deafened": False
                },
                {
                    "name": "Bob",
                    "avatar": "https://i.pravatar.cc/150?img=2",
                    "status": "online",
                    "webcam": False,
                    "stream": True,
                    "muted": True,
                    "deafened": False,
                    "server_muted": False,
                    "server_deafened": False
                },
                {
                    "name": "Charlie",
                    "avatar": "https://i.pravatar.cc/150?img=3",
                    "status": "idle",
                    "webcam": False,
                    "stream": False,
                    "muted": False,
                    "deafened": True,
                    "server_muted": False,
                    "server_deafened": False
                }
            ],
            "count": 3
        },
        "🎮 Gaming": {
            "members": [
                {
                    "name": "Dave",
                    "avatar": "https://i.pravatar.cc/150?img=4",
                    "status": "dnd",
                    "webcam": True,
                    "stream": True,
                    "muted": True,
                    "deafened": True,
                    "server_muted": False,
                    "server_deafened": False
                },
                {
                    "name": "Eve",
                    "avatar": "https://i.pravatar.cc/150?img=5",
                    "status": "online",
                    "webcam": False,
                    "stream": False,
                    "muted": False,
                    "deafened": False,
                    "server_muted": True,
                    "server_deafened": False
                }
            ],
            "count": 2
        },
        "🎶 Musique": {
            "members": [
                {
                    "name": "Frank",
                    "avatar": "https://i.pravatar.cc/150?img=6",
                    "status": "online",
                    "webcam": True,
                    "stream": False,
                    "muted": False,
                    "deafened": False,
                    "server_muted": False,
                    "server_deafened": False
                }
            ],
            "count": 1
        }
    }
