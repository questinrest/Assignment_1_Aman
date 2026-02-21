import os
import re
import hashlib
import pymupdf
from typing import List, Dict
from pathlib import Path
from src.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from src.utils import is_index_exists

# computing hash value of a file
def compute_file_hash(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()



## basic preprocesing

def preprocess_text(text:str) -> str:
    return re.sub(r'[.…]{2,}|\s+', " ", text)

    


## load pdf
def load_pdf(file_path : str) -> List[Dict]:
    path = Path(file_path)
    if not path.exists():
        print(f"Path does not exist")
    pages = []
    reader = pymupdf.open(path)

    for page_no, page in enumerate(reader):
        page_text = page.get_text()
        if page_text:
            pages.append(
                {
                    'page_no' : page_no,
                    'text' : preprocess_text(page_text).strip()
                }
            )
    return pages

# chunk page wise, with chunk size and overlap
def chunk_page(file_path : str, chunk_size : int = CHUNK_SIZE, overlap : int = CHUNK_OVERLAP) -> List[Dict]:
    doc = load_pdf(file_path=file_path)
    
    full_text = ""
    page_no_record = []

    for page in doc:
        if full_text:
            full_text += " "
            page_no_record.append(page['page_no'])
        full_text += page['text']
        page_no_record.extend([page['page_no']]*len(page['text']))

    chunks = []
    start = 0

    while start < len(full_text):
        end = min(start + chunk_size, len(full_text))
        chunk = full_text[start:end].strip()

        if chunk:
            page_no = sorted(set(page_no_record[start:end]))
            chunks.append({
                "page_no" : page_no,
                "chunk_text" : chunk
            })
        
        start += chunk_size - overlap
    
    return chunks

## preparing the chunks with more metadata for upsert
def ingest(file_path: str) -> List[Dict]:
    file_name = Path(file_path).name

    # if is_ingested(file_path=file_path): ## commented out, as not using this approach
    #     return 0 ## reason given in hash.ipynb
    hash_val = compute_file_hash(file_path=file_path)
    

    chunks = chunk_page(file_path=file_path)
    ready_to_embed_chunks = []

    for idx, chunk in enumerate(chunks):
        page_no = ",".join(str(p) for p in chunk['page_no'])
        ready_to_embed_chunks.append(
            {
                "id": f"chunk-{idx}-{file_name}",
                "page_no": page_no,
                "source": file_name,
                "chunk_text": chunk['chunk_text'],
                "source_hash_value" : hash_val
            }
        )

    return ready_to_embed_chunks













# if __name__ == '__main__':
#     result = ingest("docs\HR Handbook 2025 for website.pdf")
#     print(result)