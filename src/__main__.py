import sys
import os

# Proje kök dizinini sys.path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import app, db_client, cron_client, birthday_service, knowledge_service, chat_manager
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
from src.core.logger import logger
from dotenv import load_dotenv

def main():
    """Cemil Bot'u başlatan ana fonksiyon."""
    load_dotenv()
    
    print("\n" + "="*60)
    print("           CEMIL BOT - HIZLI BAŞLATMA (PROD)")
    print("="*60 + "\n")

    # 1. Veritabanı
    logger.info("[>] Veritabanı kontrol ediliyor...")
    db_client.init_db()

    # 2. Cron
    logger.info("[>] Zamanlayıcılar başlatılıyor...")
    cron_client.start()
    birthday_service.schedule_daily_check(hour=9, minute=0)

    # 3. RAG
    logger.info("[>] Bilgi Küpü indeksleniyor...")
    asyncio.run(knowledge_service.process_knowledge_base())

    # 4. Slack
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        logger.error("[X] SLACK_APP_TOKEN eksik!")
        return

    logger.info("[>] Slack Bağlantısı kuruluyor...")
    
    # Başlangıç Mesajı
    startup_channel = os.environ.get("SLACK_STARTUP_CHANNEL")
    if startup_channel:
        try:
             chat_manager.post_message(
                channel=startup_channel,
                text="🚀 Cemil Bot başarıyla başlatıldı ve göreve hazır!"
            )
        except Exception:
            pass

    print("\n" + "="*60)
    print("           BOT ÇALIŞIYOR - CTRL+C ile durdurun")
    print("="*60 + "\n")

    handler = SocketModeHandler(app, app_token)
    handler.start()

if __name__ == "__main__":
    main()
