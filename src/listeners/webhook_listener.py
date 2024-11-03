# File: src/listeners/webhook_listener.py
from flask import Flask, request
import threading
from cflow.automation_listener_base import AutomationListener
from cflow.logger import log

class WebhookListener(AutomationListener):
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initializes the WebhookListener with the given host and port.

        :param host: Host address where the webhook server will run.
        :param port: Port number where the webhook server will listen.
        """
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.app = Flask(__name__)

        @self.app.route("/webhook", methods=["POST"])
        def handle_webhook():
            content_length = request.content_length
            if content_length is None:
                log.error("Received webhook with no content length.")
                return "No content", 400

            post_data = request.get_data().decode('utf-8')
            log.info(f"Received webhook data: {post_data}")
            return "Webhook received", 200

    def start(self):
        """
        Starts the webhook listener in a separate thread using Flask.
        """
        def run_server():
            log.info(f"Starting WebhookListener at http://{self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

        self.thread = threading.Thread(target=run_server)
        self.thread.daemon = True
        self.thread.start()
        log.info("Webhook listener thread started.")

    def stop(self):
        """
        Stops the webhook listener.
        """
        # Since Flask does not have a native shutdown mechanism from another thread,
        # we would need a more complex approach, but we can stop the thread for now.
        if self.thread:
            log.info("Stopping WebhookListener...")
            self.thread.join()
            log.info("Webhook listener thread stopped.")

# Usage Example
# --------------------------------------------------------
# This is an example of how to use the WebhookListener class.
#
# listener = WebhookListener(host="0.0.0.0", port=9000)
# listener.start()
#
# To stop the listener, call:
# listener.stop()
# --------------------------------------------------------
