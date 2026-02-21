from pinecone import Pinecone
from src.config import (PINECONE_API_KEY, 
                        PINECONE_INDEX_NAME, 
                        PINECONE_RERANKER_MODEL,
                        TOP_K, 
                        TOP_N, 
                        PINECONE_NAMESPACE)
from typing import List, Dict


pc = Pinecone(api_key=PINECONE_API_KEY)

def search_vector_db_reranker(namespace : str,
                            query : str,
                            index_name : str = PINECONE_INDEX_NAME,
                            rerank_model : str = PINECONE_RERANKER_MODEL,
                            top_k : int = TOP_K,
                            top_n : int = TOP_N) -> List[Dict]:
    
    index = pc.Index(index_name)

    results = index.search(
    namespace=namespace, 
    query={
        "inputs": {"text": query}, 
        "top_k": top_k
    },
    rerank={
        "model": rerank_model,
        "top_n": 5,
        "rank_fields": ["chunk_text"]
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
    