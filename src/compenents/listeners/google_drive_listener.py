# src/listeners/google_drive_listener.py
import threading
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
from core.listener.listener_base import AutomationListener
from core.logger import log


class GoogleDriveListener(AutomationListener):
    def __init__(self, folder_id: str, credentials_file: str, polling_interval: int = 60):
        """
        Initializes the GoogleDriveListener to monitor a specific Google Drive folder for new files.

        :param folder_id: The ID of the Google Drive folder to monitor.
        :param credentials_file: Path to the service account credentials file.
        :param polling_interval: Interval (in seconds) at which to poll the folder for new files.
        """
        self.folder_id = folder_id
        self.credentials_file = credentials_file
        self.polling_interval = polling_interval
        self.thread = None
        self.running = False

        # Setup Google Drive API credentials
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Authenticates with the Google Drive API using the provided service account credentials.

        :return: Google Drive API service instance.
        """
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service

    def start(self):
        """
        Starts the Google Drive folder listener in a separate thread.
        """
        def monitor_folder():
            log.info(f"Starting GoogleDriveListener for folder ID: {self.folder_id}")
            self.running = True
            known_files = set()

            while self.running:
                try:
                    # Query for files in the specified folder
                    results = self.service.files().list(
                        q=f"'{self.folder_id}' in parents",
                        pageSize=100,
                        fields="files(id, name)"
                    ).execute()
                    items = results.get('files', [])

                    # Check for new files
                    for item in items:
                        if item['id'] not in known_files:
                            known_files.add(item['id'])
                            log.info(f"New file detected: {item['name']}")

                except Exception as e:
                    log.error(f"Error while polling Google Drive folder: {e}")

                time.sleep(self.polling_interval)

        self.thread = threading.Thread(target=monitor_folder)
        self.thread.daemon = True
        self.thread.start()
        log.info("Google Drive listener thread started.")

    def stop(self):
        """
        Stops the Google Drive folder listener.
        """
        log.info("Stopping GoogleDriveListener...")
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("Google Drive listener thread stopped.")


# Usage Example
# --------------------------------------------------------
# This is an example of how to use the GoogleDriveListener class.
#
# listener = GoogleDriveListener(folder_id="YOUR_FOLDER_ID", credentials_file="path/to/credentials.json")
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
