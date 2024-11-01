# Conector específico: TelegramConnector
from cflow.connector import ConnectorBase
from logger import log

class TelegramConnector(ConnectorBase):
    def __init__(self, name, description=None, token=None, chat_id=None):
        super().__init__(name, description if description else "Sends notifications via Telegram")
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def connect(self):
        log.info(f"Ready to send Telegram notifications to chat ID: {self.chat_id}")

    def notify(self, message="Workflow completed successfully."):
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        response = requests.post(self.base_url, json=payload)
        log.info(f"Notification sent to Telegram - Status Code: {response.status_code}")
