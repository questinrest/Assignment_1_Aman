from typing import List, Dict
from langchain_groq import ChatGroq
from src.config import (
    OPENAI_MODEL_GROQ,
    TEMPERATURE,
    MAX_TOKENS,
    MAX_RETRIES,
    GROQ_API_KEY
)



llm = ChatGroq(
    model=OPENAI_MODEL_GROQ,
    api_key=GROQ_API_KEY,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    max_retries=MAX_RETRIES
)




def context_build(retrieved_chunks: List[Dict]):
    l = []
    for idx, chunk in enumerate(retrieved_chunks):
        chunk_text = chunk.get("chunk_text", "")
        page_no = chunk.get("page_no", "")
        source = chunk.get("source", "not available")
        if page_no:
            page_label = f"p.{page_no}"
        else:
            page_label = ""
        l.append(f"[{idx}] (source:{source}{page_label}\n{chunk_text})")
    return "\n\n".join(l)


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I don't have enough information to answer that."

CITATION RULES:
- Each context chunk is labeled [1], [2], etc. with its source document and page number(s).
- When you use information from a chunk, cite it inline like [1], [2], etc.
- At the end of your answer, add a "References" section listing each cited source with page numbers.
- Format: [n] source_filename, p.X

Example: The offer letter must be accepted within ten days of issuance [1], and it remains valid for three months [2]. Selected candidates are required to undergo a pre-employment medical check-up at the designated lab [3], and employment may be terminated without notice if false information is discovered later [4].

References:
[1] HR Handbook 2025 for website.pdf, p.10
[2] HR Handbook 2025 for website.pdf, p.10
[3] HR Handbook 2025 for website.pdf, p.10
[4] HR Handbook 2025 for website.pdf, p.10"""



def generate_answer(query: str, chunks: List[Dict]) -> str:
    context = context_build(chunks)

    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Context:\n{context}\n\n---\nQuestion: {query}"),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content