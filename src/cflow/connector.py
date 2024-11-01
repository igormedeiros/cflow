# src/cflow/connector.py

import pandas as pd
import requests
from logger import log

class ConnectorBase:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def connect(self):
        log.info(f"Connecting using: {self.name}")
