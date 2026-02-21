from pinecone import Pinecone
from src.config import (PINECONE_API_KEY, 
                        PINECONE_INDEX_NAME, 
                        TOP_K, 
                        PINECONE_NAMESPACE)
from typing import List, Dict



pc = Pinecone(api_key=PINECONE_API_KEY)

def search_vector_db(namespace : str,
                    query : str = "Explain about Promotion, Upgradation, And Career Progression Process",
                    index_name : str = PINECONE_INDEX_NAME,
                    top_k : int = TOP_K) -> List[Dict]:
    
    index = pc.Index(index_name)

    results = index.search(
    namespace=namespace, 
    query={
        "inputs": {"text": query}, 
        "top_k": top_k
    },
    fields=["source", "chunk_text", "page_no"]
)
    retreived = []

    for r in results.get("result", {}).get("hits", {}):
        d = {}
        d['id'] = r.get("_id", "")
        d['score'] = r.get("_score", 0)
        d['chunk_text'] = r.get("fields", {}).get("chunk_text")
        d['page_no'] = r.get("fields", {}).get("page_no", "")
        d['source'] = r.get("fields", {}).get("source", "")
        retreived.append(d)
    
    return retreived
    