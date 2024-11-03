# src/listeners/local_folder_listener.py
import os
import time
import threading
from cflow.automation_listener_base import AutomationListener
from cflow.logger import log


class LocalFolderListener(AutomationListener):
    def __init__(self, folder_path: str, polling_interval: int = 60):
        """
        Initializes the LocalFolderListener to monitor a specific folder for newly created files.

        :param folder_path: The path to the folder to monitor.
        :param polling_interval: Interval (in seconds) at which to poll the folder for new files.
        """
        self.folder_path = folder_path
        self.polling_interval = polling_interval
        self.thread = None
        self.running = False

    def start(self):
        """
        Starts the folder listener in a separate thread.
        """
        def monitor_folder():
            log.info(f"Starting LocalFolderListener for folder: {self.folder_path}")
            self.running = True
            known_files = set(os.listdir(self.folder_path))

            while self.running:
                try:
                    current_files = set(os.listdir(self.folder_path))
                    new_files = current_files - known_files

                    for new_file in new_files:
                        log.info(f"New file detected: {new_file}")
                        known_files.add(new_file)

                except Exception as e:
                    log.error(f"Error while monitoring folder '{self.folder_path}': {e}")

                time.sleep(self.polling_interval)

        self.thread = threading.Thread(target=monitor_folder)
        self.thread.daemon = True
        self.thread.start()
        log.info("Local folder listener thread started.")

    def stop(self):
        """
        Stops the folder listener.
        """
        log.info("Stopping LocalFolderListener...")
        self.running = False
        if self.thread:
            self.thread.join()
            log.info("Local folder listener thread stopped.")


# Usage Example
# --------------------------------------------------------
# This is an example of how to use the LocalFolderListener class.
#
# listener = LocalFolderListener(folder_path="/path/to/your/folder")
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
