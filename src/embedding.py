import time
from typing import List, Dict
from pinecone import Pinecone
from src.config import (
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
    PINECONE_EMBEDDING_MODEL,
    BATCH_SIZE
)

pc = Pinecone(
    api_key= PINECONE_API_KEY
)

## checking if the index is created or not

def get_or_create_index(PINECONE_IND : str = PINECONE_INDEX_NAME,
                          cloud : str = PINECONE_CLOUD,
                          region : str = PINECONE_REGION,
                          embed_model : str = PINECONE_EMBEDDING_MODEL):
    if not pc.has_index(PINECONE_IND):
        pc.create_index_for_model(
            name = PINECONE_IND,
            cloud= cloud,
            region= region,
            embed={"model" : embed_model, "field_map" : {'text' : "chunk_text"}})
        print(f"Index- {PINECONE_INDEX_NAME} is creating...")
        while not pc.describe_index(PINECONE_INDEX_NAME).status.get('ready', False):
            time.sleep(1)
        print(f"Index- {PINECONE_INDEX_NAME} is created")
    else:
        print(f"Index- {PINECONE_INDEX_NAME} is already created")

    return pc.Index(PINECONE_INDEX_NAME)


def duplicate_exists_(namespace: str, source_hash: str) -> bool:
    index = get_or_create_index()

    response = index.search(
        namespace=namespace,
        query={
            "inputs": {
                "text": "checking"
            },
            "top_k": 1,
            "filter": {
                "source_hash_value": {"$eq": source_hash}
            }
        }
    )
    return len(response.result.hits) > 0


## added with namspace
def upsert_chunks(chunks: List[Dict],namespace : str ,index_name: str = PINECONE_INDEX_NAME, batch_size : int = BATCH_SIZE):
    index = get_or_create_index(index_name)

    records = []

    for chunk in chunks:
        records.append({
            "_id": chunk["id"],
            "chunk_text": chunk["chunk_text"],
            "source": chunk["source"],
            "page_no": chunk["page_no"],
            "source_hash_value" : chunk['source_hash_value']
        })

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        index.upsert_records(namespace=namespace, records=batch)

    print(f"All chunks upserted to {index_name} and {namespace} namespace.")
    return len(records)

