# src/listeners/telegram_message_listener.py
import time
import threading
import requests
from core.listener.listener_base import AutomationListener
from core.logger import log


class TelegramMessageListener(AutomationListener):
    def __init__(self, bot_token: str, chat_id: str, target_message: str, polling_interval: int = 10):
        """
        Initializes the TelegramMessageListener to monitor a specific Telegram chat for a given message.

        :param bot_token: The Telegram bot token to access the Telegram API.
        :param chat_id: The ID of the chat to monitor.
        :param target_message: The specific message to listen for.
        :param polling_interval: Interval (in seconds) at which to poll the chat for new messages.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.target_message = target_message
        self.polling_interval = polling_interval
        self.thread = None
        self.running = False
        self.offset = None

    def start(self):
        """
        Starts the Telegram message listener in a separate thread.
        """
        def monitor_messages():
            log.info(f"Starting TelegramMessageListener for chat ID: {self.chat_id}")
            self.running = True

            while self.running:
                try:
                    url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                    params = {"timeout": 100, "offset": self.offset}
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    updates = response.json()["result"]

                    for update in updates:
                        self.offset = update["update_id"] + 1
                        if "message" in update and "text" in update["message"]:
                            chat_id = update["message"]["chat"]["id"]
                            message_text = update["message"]["text"]

                            if chat_id == int(self.chat_id) and message_text == self.target_message:
                                log.info(f"Target message received: {message_text}")

                except requests.exceptions.RequestException as e:
                    log.error(f"Error while polling Telegram messages: {e}")

                time.sleep(self.polling_interval)

        self.thread = threading.Thread(target=monitor_messages)
        self.thread.daemon = True
        self.thread.start()
        log.info("Telegram message listener thread started.")

    def stop(self):
        """
        Stops the Telegram message listener.
        """
        log.info("Stopping TelegramMessageListener...")
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("Telegram message listener thread stopped.")


# Usage Example
# --------------------------------------------------------
# This is an example of how to use the TelegramMessageListener class.
#
# listener = TelegramMessageListener(bot_token="YOUR_BOT_TOKEN", chat_id="YOUR_CHAT_ID", target_message="/start")
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
