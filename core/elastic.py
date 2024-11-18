import os
from elasticsearch import Elasticsearch, exceptions
from dotenv import load_dotenv

load_dotenv()
# Create an Elasticsearch client instance connecting to localhost on port 9200 using HTTP
es = Elasticsearch([{'host': os.getenv("ELASTICSEARCH_HOST"), 'port': 9200, 'scheme': 'http'}])

# Define the index mapping with specific properties
index_mapping = {
    "mappings": {
        "properties": {
            "topic": {"type": "text"},  
            "information": {"type": "text"}, 
            "vector": {"type": "dense_vector", "dims": 384}, 
            "timestamp": {"type": "date"}
        }
    }
}

# Check if the index "chatbot_info" exists; if not, create it with the defined mapping
if not es.indices.exists(index="chatbot_info"):
    es.indices.create(index="chatbot_info", body=index_mapping)

# Attempt to retrieve Elasticsearch cluster information to verify the connection
try:
    es.info()
    print("Connected to Elasticsearch")
except exceptions.ConnectionError:
    print("Could not connect to Elasticsearch")
