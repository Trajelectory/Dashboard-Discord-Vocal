# 🎤 Discord Voice Monitor
<img width="1906" height="914" alt="image" src="https://github.com/user-attachments/assets/64c0c46e-e609-4cb1-9c70-5e61838ee914" />
<img width="1920" height="1455" alt="FireShot Capture 004 - Statistiques Vocales Discord - localhost" src="https://github.com/user-attachments/assets/4fbf81bd-082b-4681-bdd5-49adcd13ff8a" />

Discord Voice Monitor est un système complet de monitoring qui surveille l'activité des utilisateurs dans les salons vocaux Discord. Il expose ces données via une interface web moderne avec mises à jour en temps réel (WebSocket) et une API REST complète.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-purple.svg)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### Ce que fait l'application

- 👥 Surveille les connexions/déconnexions des membres
- 🎤 Détecte les changements d'état (mute, deafen, webcam, streaming)
- 📊 Enregistre des statistiques détaillées (durée des sessions, records)
- 🌐 Fournit une interface web en temps réel
- 🔌 Expose une API REST complète
- 💾 Persiste les données dans SQLite

## ✨ Fonctionnalités

### Composants principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée, lance le bot et le serveur web |
| `discord_bot.py` | Bot Discord, surveillance des salons vocaux |
| `web_server.py` | Serveur Flask avec WebSocket et API REST |
| `activity_logger.py` | Enregistrement de tous les événements |
| `stats_tracker.py` | Statistiques avec persistance SQLite |
| `health_monitor.py` | Monitoring de la santé du système |
| `test_data.py` | Données de test pour le mode démo |
| `config.py` | Configuration (tokens, IDs, paramètres) |

### Monitoring en temps réel

- **Détection des événements**
  - Connexion/Déconnexion d'un salon vocal
  - Changement de salon (move)
  - Activation/Désactivation du micro
  - Activation/Désactivation du casque (deafen)
  - Démarrage/Arrêt du streaming
  - Activation/Désactivation de la webcam
  - Mute/Unmute par le serveur

### Profils utilisateurs complets

Pour chaque membre en vocal, récupération de :
- Informations d'identité (username, discriminator, display name)
- Avatars (serveur, profil, par défaut)
- Statut (online, idle, dnd, offline) sur desktop/mobile/web
- Activités en cours (Spotify, jeux, streaming personnalisé)
- Rôles et permissions
- Dates importantes (création compte, arrivée serveur, nitro boost)
- État vocal complet

### Statistiques avancées

- **Sessions vocales**
  - Durée totale par jour/semaine/mois
  - Nombre de sessions
  - Durée moyenne des sessions
  - Canaux visités

- **Records**
  - Session la plus longue du jour
  - Session la plus longue de la semaine
  - Session la plus longue du mois
  - Record absolu (all-time)

- **Classements**
  - Top utilisateurs du jour
  - Top utilisateurs de la semaine
  - Sessions en cours avec durée actuelle

### Interface Web

- Dashboard moderne et responsive
- Mises à jour en temps réel via WebSocket
- Historique des logs d'activité
- Page de statistiques détaillées
- Documentation API intégrée

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Un bot Discord configuré ([Guide Discord Developer Portal](https://discord.com/developers/applications))
- Les tokens et IDs nécessaires

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/Trajelectory/Dashboard-Discord-Vocal.git
cd discord-voice-monitor
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

Dépendances principales :
```
discord.py>=2.0.0
flask>=2.0.0
flask-socketio>=5.0.0
python-socketio>=5.0.0
```

3. **Créer le fichier de configuration**

Créez un fichier `config.py` :
```python
# Discord Configuration
DISCORD_TOKEN = "votre_token_discord_bot"
VOICE_CHANNEL_IDS = [123456789, 987654321]  # IDs des salons à surveiller

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
SECRET_KEY = "votre_clé_secrète_flask"

# Database
DATABASE_PATH = "discord_stats.db"

# Mode de test (utilise des données fictives)
TEST_MODE = False
```

4. **Lancer l'application**
```bash
python main.py
```

L'application sera accessible sur `http://localhost:5000`

## ⚙️ Configuration

### Obtenir le token Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application
3. Dans l'onglet "Bot", créez un bot et copiez le token
4. Activez les **Privileged Gateway Intents** :
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent (optionnel)

### Trouver les IDs des salons vocaux

1. Activez le mode développeur Discord (Paramètres → Avancé → Mode développeur)
2. Clic droit sur un salon vocal → Copier l'identifiant
3. Ajoutez l'ID dans `VOICE_CHANNEL_IDS`

### Inviter le bot sur votre serveur

Utilisez cette URL (remplacez `CLIENT_ID` par l'ID de votre application) :
```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=2147516416&scope=bot
```

Permissions nécessaires :
- View Channels
- Connect (aux vocaux)
- Read Message History

## 📖 Utilisation

### Interface Web

Accédez à `http://localhost:5000` pour :
- Voir en temps réel qui est connecté
- Consulter l'historique des événements
- Accéder aux statistiques détaillées

### Mode démo

Pour tester sans connexion Discord, activez le mode test :
```python
# config.py
TEST_MODE = True
```
Le système utilisera alors des données fictives.

## 📊 Statistiques

### Données trackées

Le système enregistre en SQLite :

- **Sessions complètes**
  - Membre, heure de début/fin, durée
  - Canaux visités
  - État actif/terminé

- **Records**
  - Longest session today/week/month/ever
  - Détenteur du record
  - Date du record

### Accès aux statistiques

**API** : `/stats` (page web) ou WebSocket event `get_stats`

**Exemples de données** :
```json
{
  "all_stats": {
    "Alice": {
      "total_time": 7200,
      "session_count": 3,
      "average_session": 2400,
      "channels_visited": ["Salon 1", "Salon 2"]
    }
  },
  "top_users": [
    { "member": "Alice", "total_time": 7200 },
    { "member": "Bob", "total_time": 3600 }
  ],
  "records": {
    "longest_session_today": {
      "member": "Alice",
      "duration": 5400,
      "date": "2025-01-01T10:00:00"
    }
  }
}
```

## 🛠️ Technologies

- **Backend**
  - Python 3.8+
  - Discord.py (Bot Discord)
  - Flask (Serveur web)
  - Flask-SocketIO (WebSocket temps réel)
  - SQLite (Base de données)

- **Frontend**
  - HTML5 / CSS3 / JavaScript
  - Socket.IO Client (WebSocket)

## 🤝 Contribution

Les contributions sont les bienvenues ! 

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Discord.py](https://github.com/Rapptz/discord.py) pour l'excellent wrapper Discord
- [Flask](https://flask.palletsprojects.com/) pour le framework web
- [Socket.IO](https://socket.io/) pour le WebSocket temps réel

---

<p align="center">
  Développé avec ❤️ pour la communauté Discord
</p>

<p align="center">
  <a href="#-table-des-matières">Retour en haut ⬆️</a>
</p>
