import os
import hashlib
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
    """Index chunks with DOM metadata. Ensures vector IDs never collide."""
    vectors = []

    # Create hashed namespace prefix so URL never causes ID collisions
    prefix = hashlib.md5(url_prefix.encode()).hexdigest()[:12]

    for i, chunk in enumerate(chunks):

        # UNIQUE vector id
        vector_id = f"{prefix}-{i}"

        # Base metadata
        metadata = {
            "text": chunk,
            "chunk_id": i,
            "url": url_prefix
        }

        # Attach DOM metadata (html, tag, class, id, path)
        if metadata_list and i < len(metadata_list):
            metadata.update(metadata_list[i])

        vectors.append(
            (vector_id, model.encode(chunk).tolist(), metadata)
        )

    # Upload to Pinecone
    index.upsert(vectors=vectors)

    print("\n===== DEBUG METADATA SENT TO PINECONE =====")
    print(vectors[0][2])
    print("============================================\n")

    print(f"📤 Indexed {len(vectors)} chunks to Pinecone")


def semantic_search(query: str, top_k=10):
    """Query Pinecone and return DOM-aware chunk results."""
    from utils.chunker import tokenizer as chunk_tokenizer

    query_emb = model.encode(query).tolist()
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    matches = results.get("matches", [])

    formatted = []
    seen_texts = set()

    for match in matches:
        metadata = match.get("metadata", {})

        print("\n===== DEBUG METADATA RETURNED FROM PINECONE =====")
        print(metadata)
        print("=================================================\n")

        text = metadata.get("text", "")
        if not text or text in seen_texts:
            continue

        seen_texts.add(text)

        html_snippet = metadata.get("html", "")
        url = metadata.get("url", "")
        path = metadata.get("path", "home")

        # Token truncation
        tokens = chunk_tokenizer.encode(text, add_special_tokens=False)
        truncated_text = chunk_tokenizer.decode(tokens[:500]) if len(tokens) > 500 else text

        score_percent = round(match["score"] * 100, 2)

        formatted.append({
            "rank": len(formatted) + 1,
            "score": score_percent,
            "match_percentage": f"{int(score_percent)}%",
            "tokens": min(len(tokens), 500),

            # Main content
            "chunk_text": truncated_text,
            "html": html_snippet,

            # DOM metadata
            "tag_name": metadata.get("tag_name", ""),
            "tag_id": metadata.get("tag_id", ""),
            "tag_class": metadata.get("tag_class", ""),

            # Navigation
            "url": url,
            "path": f"/{path}" if path else "/home"
        })

    return formatted[:top_k]
