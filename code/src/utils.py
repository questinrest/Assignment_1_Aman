from pinecone import Pinecone
from src.config import PINECONE_API_KEY, PINECONE_INDEX_NAME



pc = Pinecone(api_key=PINECONE_API_KEY)

def is_index_exists(index_name = PINECONE_INDEX_NAME):
    if index_name in pc.list_indexes().names():
        return True
    return False
