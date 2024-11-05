import os

from dotenv import load_dotenv

from components.connectors.telegram.telegram_connector import TelegramConnector
from core.logger import log


def test_telegram():
    # Carrega e mostra variáveis do .env
    print("\n=== Loading Environment Variables ===")
    load_dotenv()

    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    print(f"TELEGRAM_BOT_TOKEN: {'*' * 10}{token[-5:] if token else 'Not found'}")
    print(f"TELEGRAM_CHAT_ID: {chat_id if chat_id else 'Not found'}")
    print("===================================\n")

    try:
        telegram = TelegramConnector(
            token=token,
            chat_id=chat_id
        )

        telegram.connect()
        success = telegram.send_message("Oi, Igor. Eu sou seu robô de automação! 🤖")

        if success:
            log.info("Message sent successfully!")
        else:
            log.error("Failed to send message!")

        telegram.disconnect()

    except Exception as e:
        log.error(f"Test error: {str(e)}")
        raise


if __name__ == "__main__":
    test_telegram()