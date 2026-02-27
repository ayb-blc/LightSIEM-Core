from elasticsearch import Elasticsearch
import os
import sys

# Retrieve environment variables from Docker Compose
# Use 'localhost' if running locally, or 'elasticsearch' (service name) if running in Docker
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", "9200")
ES_SCHEME = "http"

class StorageEngine:
    def __init__(self):
        # Initialize the Elasticsearch client
        self.client = Elasticsearch(
            f"{ES_SCHEME}://{ES_HOST}:{ES_PORT}",
            verify_certs=False 
        )
    
    def is_connected(self):
        try:
            return self.client.ping()
        except Exception:
            return False

    def save_log(self, index_name: str, document: dict):
        """
        Writes the log to the specified index (table).
        """
        try:
            res = self.client.index(index=index_name, document=document)
            return res['result']
        except Exception as e:
            print(f"[STORAGE ERROR] Failed to write log : {e}", file=sys.stderr)
            return None

# Singleton Pattern: A single connection throughout the application
es_service = StorageEngine()