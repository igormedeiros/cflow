# src/cflow/connector.py

import pandas as pd
import requests

class ConnectorBase:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def connect(self):
        print(f"Connecting using: {self.name}")
