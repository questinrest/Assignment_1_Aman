import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()


## API KEYS

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


## ingestion params

CHUNK_SIZE : int = 500
CHUNK_OVERLAP : int = 60
BATCH_SIZE : int = 96 # max 
TOP_K : int = 5
TOP_N : int = 4

## Pinecone Specific

PINECONE_INDEX_NAME : str = 'rag-pipeline-reranker'
PINECONE_CLOUD : str = "aws"
PINECONE_REGION : str = "us-east-1"
PINECONE_EMBEDDING_MODEL : str = "llama-text-embed-v2"
PINECONE_RERANKER_MODEL : str = "bge-reranker-v2-m3"
PINECONE_NAMESPACE : str = ""


## LLM params
OPENAI_MODEL_GROQ : str = "openai/gpt-oss-120b"
TEMPERATURE : float = 0.0
MAX_TOKENS : int = None



