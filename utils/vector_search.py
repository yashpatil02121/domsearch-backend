import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"))

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if not exists
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

def index_chunks(chunks):
    vectors = [(f"id-{i}", model.encode(chunk).tolist(), {"text": chunk}) for i, chunk in enumerate(chunks)]
    index.upsert(vectors=vectors)

def semantic_search(query: str, top_k=10):
    query_emb = model.encode(query).tolist()
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]
