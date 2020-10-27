import os
from pymongo import MongoClient
import atexit


mongodb_db = os.environ['TX_CAPITAL_DB_NAME']
mongodb_user = os.environ['TX_CAPITAL_DB_USERNAME']
mongodb_password = os.environ['TX_CAPITAL_DB_PASSWORD']
mongodb_cluster_url = os.environ['TX_CAPITAL_DB_CLUSTER_URL']   # ex. "cluster0.xxxxx" in the prefix of your connection url

client = MongoClient(f'mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_cluster_url}.mongodb.net/{mongodb_db}?retryWrites=true&w=majority')
atexit.register(client.close)
db = client[mongodb_db]