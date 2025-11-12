import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"))

pc = Pinecone(api_key=PINECONE_API_KEY)

# Ensure index exists
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

index = pc.Index(INDEX_NAME)

def index_chunks(chunks, url_prefix="", metadata_list=None):
    """Index chunks (≤500 tokens each) with metadata."""
    vectors = []
    for i, chunk in enumerate(chunks):
        # Create unique ID using URL prefix to avoid conflicts between different websites
        vector_id = f"{url_prefix}-{i}" if url_prefix else f"id-{i}"
        
        # Base metadata
        metadata = {
            "text": chunk,
            "chunk_id": i,
            "url": url_prefix
        }
        
        # Add additional metadata if provided (HTML, path, etc.)
        if metadata_list and i < len(metadata_list):
            metadata.update(metadata_list[i])
        
        vectors.append(
            (vector_id, model.encode(chunk).tolist(), metadata)
        )
    index.upsert(vectors=vectors)
    print(f"📤 Indexed {len(vectors)} chunks to Pinecone")

def semantic_search(query: str, top_k=10):
    """Return up to top_k unique results (each ≤500 tokens)."""
    query_emb = model.encode(query).tolist()
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    matches = results.get("matches", [])

    formatted = []
    seen_texts = set()  # Track unique chunks to avoid duplicates
    
    for i, match in enumerate(matches):
        metadata = match["metadata"]
        text = metadata.get("text", "")
        url = metadata.get("url", "")
        html_snippet = metadata.get("html", "")
        path = metadata.get("path", "/")
        
        # Skip duplicates
        if text in seen_texts:
            continue
        seen_texts.add(text)
        
        tokens = model.tokenizer.encode(text)
        
        # Ensure each chunk is ≤500 tokens
        if len(tokens) > 500:
            truncated_text = model.tokenizer.decode(tokens[:500])
            truncated_html = html_snippet[:500] if html_snippet else ""
        else:
            truncated_text = text
            truncated_html = html_snippet
        
        # Calculate match percentage (score is typically 0-1, convert to percentage)
        match_percentage = round(match["score"] * 100, 0)
        
        # Use HTML as chunk_text if available (like in the UI mockup)
        display_text = truncated_html if truncated_html else truncated_text
        
        formatted.append({
            "rank": len(formatted) + 1,
            "score": round(match["score"] * 100, 2),
            "match_percentage": f"{match_percentage}% match",
            "tokens": min(len(tokens), 500),
            "chunk_text": display_text,
            "url": url,
            "path": f"Path: /{path}" if path and path != "/" else "Path: /home",
            "html": truncated_html
        })

    print(f"🔎 Returning {len(formatted)} unique results (each ≤500 tokens)")
    return formatted
