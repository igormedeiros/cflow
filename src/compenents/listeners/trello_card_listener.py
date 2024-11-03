# src/listeners/trello_card_listener.py
import threading
import time
import requests
from core.listener.listener_base import AutomationListener
from core.logger import log


class TrelloCardListener(AutomationListener):
    def __init__(self, board_id: str, api_key: str, token: str, polling_interval: int = 60):
        """
        Initializes the TrelloCardListener to monitor a specific Trello board for new cards.

        :param board_id: The ID of the Trello board to monitor.
        :param api_key: Trello API key.
        :param token: Trello API token.
        :param polling_interval: Interval (in seconds) at which to poll the board for new cards.
        """
        self.board_id = board_id
        self.api_key = api_key
        self.token = token
        self.polling_interval = polling_interval
        self.thread = None
        self.running = False

    def start(self):
        """
        Starts the Trello board listener in a separate thread.
        """
        def monitor_board():
            log.info(f"Starting TrelloCardListener for board ID: {self.board_id}")
            self.running = True
            known_cards = set()

            while self.running:
                try:
                    # Request to get all cards from the specified board
                    url = f"https://api.trello.com/1/boards/{self.board_id}/cards"
                    params = {
                        'key': self.api_key,
                        'token': self.token
                    }
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    cards = response.json()

                    # Check for new cards
                    for card in cards:
                        if card['id'] not in known_cards:
                            known_cards.add(card['id'])
                            log.info(f"New card detected: {card['name']}")

                except requests.exceptions.RequestException as e:
                    log.error(f"Error while polling Trello board: {e}")

                time.sleep(self.polling_interval)

        self.thread = threading.Thread(target=monitor_board)
        self.thread.daemon = True
        self.thread.start()
        log.info("Trello board listener thread started.")

    def stop(self):
        """
        Stops the Trello board listener.
        """
        log.info("Stopping TrelloCardListener...")
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("Trello board listener thread stopped.")


# Usage Example
# --------------------------------------------------------
# This is an example of how to use the TrelloCardListener class.
#
# listener = TrelloCardListener(board_id="YOUR_BOARD_ID", api_key="YOUR_API_KEY", token="YOUR_TOKEN")
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
