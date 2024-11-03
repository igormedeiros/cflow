# src/listeners/mautic_contact_listener.py
import time
import threading
import requests
from cflow.automation_listener_base import AutomationListener
from cflow.logger import log


class MauticContactListener(AutomationListener):
    def __init__(self, base_url: str, username: str, password: str, polling_interval: int = 60):
        """
        Initializes the MauticContactListener to monitor for newly created contacts in Mautic.

        :param base_url: The base URL of the Mautic instance.
        :param username: The username for Mautic authentication.
        :param password: The password for Mautic authentication.
        :param polling_interval: Interval (in seconds) at which to poll Mautic for new contacts.
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.polling_interval = polling_interval
        self.thread = None
        self.running = False
        self.last_contact_id = None

    def start(self):
        """
        Starts the Mautic contact listener in a separate thread.
        """
        def monitor_contacts():
            log.info(f"Starting MauticContactListener for instance: {self.base_url}")
            self.running = True

            while self.running:
                try:
                    url = f"{self.base_url}/api/contacts"
                    response = requests.get(url, auth=(self.username, self.password))
                    response.raise_for_status()
                    contacts = response.json()["contacts"]

                    if contacts:
                        latest_contact_id = max(int(contact_id) for contact_id in contacts.keys())
                        if self.last_contact_id is None or latest_contact_id > self.last_contact_id:
                            new_contacts = [contact for contact_id, contact in contacts.items() if int(contact_id) > (self.last_contact_id or 0)]
                            for new_contact in new_contacts:
                                log.info(f"New contact created: {new_contact['fields']['all']['firstname']} {new_contact['fields']['all']['lastname']}")
                            self.last_contact_id = latest_contact_id

                except requests.exceptions.RequestException as e:
                    log.error(f"Error while polling Mautic contacts: {e}")

                time.sleep(self.polling_interval)

        self.thread = threading.Thread(target=monitor_contacts)
        self.thread.daemon = True
        self.thread.start()
        log.info("Mautic contact listener thread started.")

    def stop(self):
        """
        Stops the Mautic contact listener.
        """
        log.info("Stopping MauticContactListener...")
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("Mautic contact listener thread stopped.")


# Usage Example
# --------------------------------------------------------
# This is an example of how to use the MauticContactListener class.
#
# listener = MauticContactListener(base_url="http://your-mautic-instance.com", username="your_username", password="your_password")
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
