import weaviate
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API")
)

if 'shutter-share-index' not in pc.list_indexes().names():
    pc.create_index(
        name='shutter-share-index',
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
    )
)

URL = os.getenv("WCS_URL")
APIKEY = os.getenv("WCS_API_KEY")
  

weaviate_client = weaviate.connect_to_wcs(
    cluster_url=URL,
    auth_credentials=weaviate.auth.AuthApiKey(APIKEY))

def main():
    return 1

def close_weaviate_client():
    if weaviate_client:
        weaviate_client.close()
        
import atexit
atexit.register(close_weaviate_client)