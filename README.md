# 🎤 Discord Voice Monitor
<img width="1906" height="914" alt="image" src="https://github.com/user-attachments/assets/64c0c46e-e609-4cb1-9c70-5e61838ee914" />

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Un bot Discord avec interface web en temps réel pour surveiller l'activité des salons vocaux. Visualisez qui est en vocal, qui partage son écran, qui active sa webcam, et suivez l'historique des connexions en temps réel !

![Discord Voice Monitor](https://via.placeholder.com/800x400/667eea/ffffff?text=Discord+Voice+Monitor)

## ✨ Fonctionnalités

### 🎯 Surveillance en temps réel
- 🔴 **Monitoring instantané** des salons vocaux Discord
- 📹 **Détection de webcam** avec badge et style visuel dédié
- 📡 **Détection de partage d'écran** avec effet LIVE animé
- 🔇 **Indicateurs audio** (mute/deaf) par utilisateur et serveur
- 🟢 **Statut Discord** en temps réel (en ligne, absent, ne pas déranger)

### 🌐 Interface web moderne
- ⚡ **Mises à jour instantanées** via WebSocket (pas de rafraîchissement)
- 🎨 **Design élégant** avec animations fluides
- 📱 **Responsive** et adapté mobile
- 🌙 **Prêt pour mode sombre** (facilement personnalisable)

### 📊 Monitoring système
- 💚 **Health check** en temps réel du bot et de la connexion
- 📈 **Statistiques** (uptime, clients connectés, ping)
- 🔍 **Panel de monitoring** rétractable

### 📋 Historique d'activité
- 🟢 **Logs de connexion** (qui rejoint quel salon)
- 🔴 **Logs de déconnexion** (qui quitte quel salon)
- 🟠 **Logs de déplacement** (changements de salon)
- 💾 **Historique persistant** (200 derniers événements)

### Panel de logs
```
📋 Activité récente
├─ 15:23:45 Alice a rejoint 🎧 Salon Principal
├─ 15:25:12 Bob a rejoint 🎮 Gaming
├─ 15:27:30 Alice est passé de 🎧 Salon Principal à 🎮 Gaming
└─ 15:30:00 Bob a quitté 🎮 Gaming
```

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Un compte Discord
- Un serveur Discord avec des salons vocaux

### 1. Cloner le projet

```bash
git clone https://github.com/Trajelectory/Dashboard-Discord-Vocal.git
cd discord-voice-monitor
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Ou manuellement :**
```bash
pip install discord.py flask flask-socketio
```

### 3. Créer un bot Discord

1. Allez sur https://discord.com/developers/applications
2. Créez une nouvelle application
3. Dans l'onglet **"Bot"** :
   - Créez un bot
   - Copiez le token
   - Activez les intents suivants :
     - ✅ `PRESENCE INTENT`
     - ✅ `SERVER MEMBERS INTENT`
     - ✅ `MESSAGE CONTENT INTENT` (optionnel)
4. Dans l'onglet **"OAuth2 > URL Generator"** :
   - Cochez `bot`
   - Permissions : `View Channels`, `Read Messages/View Channels`
   - Copiez l'URL générée et invitez le bot sur votre serveur

### 4. Configuration

Éditez le fichier `config.py` :

```python
# Token de votre bot Discord
DISCORD_TOKEN = "votre_token_ici"

# IDs des salons vocaux à surveiller (3 maximum recommandé)
VOICE_CHANNEL_IDS = [123456789, 987654321, 456789123]

# Configuration serveur web
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# Mode test (True = données fictives, False = vraies données)
TEST_MODE = False
```

**Pour obtenir les IDs des salons :**
1. Activez le mode développeur dans Discord (Paramètres > Avancé)
2. Clic droit sur un salon vocal > Copier l'identifiant

## 🎮 Utilisation

### Lancer le bot

```bash
python main.py
```

Vous verrez :
```
🌐 Interface web disponible sur http://localhost:5000
🤖 Démarrage du bot Discord...
✅ Bot connecté en tant que VotreBot#1234
```

### Accéder à l'interface

Ouvrez votre navigateur sur : **http://localhost:5000**

L'interface se met à jour automatiquement en temps réel !

### Accéder depuis un autre appareil

Si vous êtes sur le même réseau local :
```
http://VOTRE_IP_LOCAL:5000
```

Exemple : `http://192.168.1.48:5000`

## 📁 Structure du projet

```
discord-voice-monitor/
├── main.py                  # Point d'entrée principal
├── config.py                # Configuration (token, IDs, paramètres)
├── discord_bot.py           # Logique du bot Discord
├── web_server.py            # Serveur Flask + WebSocket
├── health_monitor.py        # Système de monitoring
├── activity_logger.py       # Gestion des logs d'activité
├── test_data.py             # Données de test (mode démo)
├── templates/
│   └── index.html          # Template HTML
├── static/
│   ├── css/
│   │   └── style.css       # Styles CSS
│   └── js/
│       └── app.js          # JavaScript client
├── requirements.txt         # Dépendances Python
├── README.md               # Documentation
├── CHANGELOG.md            # Historique des versions
└── LICENSE                 # Licence MIT
```

## 🧪 Mode Test

Pour tester l'interface sans connexion Discord, activez le mode test dans `config.py` :

```python
TEST_MODE = True
```

Des utilisateurs fictifs avec différentes activités (webcam, stream, mute) s'afficheront automatiquement.

## ⚙️ Configuration avancée

### Personnaliser le port du serveur web

Dans `config.py` :

```python
FLASK_PORT = 8080  # Changez le port si nécessaire
```

### Ajouter plus de salons vocaux

Dans `config.py`, ajoutez simplement les IDs :

```python
VOICE_CHANNEL_IDS = [111111, 222222, 333333, 444444, 555555]
```

### Augmenter l'historique des logs

Dans `activity_logger.py` :

```python
activity_logger = ActivityLogger(max_logs=500)  # Au lieu de 200
```

## 🔌 API Endpoints

Le serveur expose plusieurs endpoints REST :

- `GET /` - Interface web principale
- `GET /health` - Health check (retourne 200 si healthy, 503 sinon)
- `GET /api/status` - Status détaillé du système (JSON)
- `GET /api/logs` - Historique complet des logs (JSON)

### Exemple d'utilisation

```bash
# Health check
curl http://localhost:5000/health

# Récupérer les logs
curl http://localhost:5000/api/logs
```

## 🛠️ Technologies utilisées

- **[Discord.py](https://discordpy.readthedocs.io/)** v2.0+ - Bibliothèque Discord pour Python
- **[Flask](https://flask.palletsprojects.com/)** v3.0+ - Framework web
- **[Flask-SocketIO](https://flask-socketio.readthedocs.io/)** - WebSocket pour mises à jour temps réel
- **HTML5/CSS3/JavaScript** - Interface utilisateur moderne

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Discord.py](https://github.com/Rapptz/discord.py) pour la bibliothèque Discord
- [Flask](https://github.com/pallets/flask) pour le framework web
- [Socket.IO](https://socket.io/) pour les WebSockets
- La communauté Discord pour l'inspiration

⭐ Si ce projet vous est utile, n'oubliez pas de mettre une étoile sur GitHub !

<p align="center">Made with ❤️ for the Discord community</p>
# Base de données (si vous en ajoutez une plus tard)
*.db
*.sqlite
*.sqlite3
