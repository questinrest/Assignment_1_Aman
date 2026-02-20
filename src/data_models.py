from pydantic import BaseModel, field_validator
from typing import List, Literal


class IngestRequest(BaseModel):
    file_path : str

    @field_validator('file_path')
    @classmethod
    def normalize_path(cls, v):
        normalized = v.replace("\\", "/")
        return normalized

class IngestResponse(BaseModel):
    source_doc : str 
    chunks : int
    message : str


class QueryRequest(BaseModel):
    query : str
    rerank : bool


class QueryResponse(BaseModel):
    answer : str
    pass