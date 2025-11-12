from transformers import AutoTokenizer
import os

model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
tokenizer = AutoTokenizer.from_pretrained(model_name)
MAX_TOKENS = int(os.getenv("MAX_TOKENS_PER_CHUNK", 500))

def chunk_text(text: str):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    for i in range(0, len(tokens), MAX_TOKENS):
        chunk = tokenizer.decode(tokens[i:i+MAX_TOKENS])
        chunks.append(chunk)
    return chunks
