from pathlib import Path
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from src.embedding import upsert_chunks, duplicate_exists_
from src.ingestion import ingest, compute_file_hash
from src.retrieval import search_vector_db
from src.reranker import search_vector_db_reranker
from src.generation import generate_answer
from src.config import PINECONE_NAMESPACE
from src.data_models import IngestRequest, IngestResponse, QueryRequest, QueryResponse, Source
from fastapi.responses import PlainTextResponse

app = FastAPI()



@app.get("/")
def health():
    return {"status" : "okay"}


# end point for document ingestion in the vector db

@app.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest, namespace = PINECONE_NAMESPACE):
    try:
        hash_val = compute_file_hash(request.file_path)
        if duplicate_exists_(namespace=namespace, source_hash=hash_val):
            return IngestResponse(
                source_doc=request.file_path,
                chunks=0,
                message="doc already exist",
            )
        ready_embed_chunks = ingest(request.file_path)

        upserted_chunks = upsert_chunks(chunks=ready_embed_chunks, namespace=namespace)

        return IngestResponse(
            source_doc=request.file_path,
            chunks=upserted_chunks,
            message="document ingested successfully",
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")




# end point for query generation

@app.post("/query", response_model=QueryResponse)
def query(request : QueryRequest, namespace = PINECONE_NAMESPACE):
    try:
        if request.rerank == True:
            related_docs = search_vector_db_reranker(query=request.query, namespace=namespace)
        else:
            related_docs = search_vector_db(query=request.query, namespace=namespace)
        def to_source(idx, chunk):
            return Source(
                source = chunk['source'],
                page_no= chunk['page_no']
            )
        sources = [to_source(idx, chunk) for idx, chunk in enumerate(related_docs)]
        

        return QueryResponse(
            answer= generate_answer(query=request.query, chunks=related_docs),
            reference= sources,
            rerank=request.rerank
        )
        #return PlainTextResponse(status_code = 200, content=generate_answer(query=request.query, chunks=related_docs))
    except Exception as e:
        raise HTTPException(status_code=500, detail= f"Error generating answer: {str(e)}")