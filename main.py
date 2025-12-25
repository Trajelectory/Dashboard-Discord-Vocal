from threading import Thread
from web_server import run_server
from discord_bot import run_bot
from config import FLASK_PORT

if __name__ == "__main__":
    # Lance le serveur Flask dans un thread séparé
    flask_thread = Thread(target=run_server)
    flask_thread.daemon = True
    flask_thread.start()
    
    print(f"🌐 Interface web disponible sur http://localhost:{FLASK_PORT}")
    print("🤖 Démarrage du bot Discord...")
    
    # Lance le bot Discord (bloquant)
    run_bot()