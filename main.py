from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from utils.html_parser import extract_text_with_structure
from utils.chunker import chunk_text
from utils.vector_search import index_chunks, semantic_search

app = FastAPI()

# not used for now but can be used for bulk indexing in the future
class IndexRequest(BaseModel):
    urls: List[str]

# index a single website
@app.post("/index")
def index_website(url: str = Query(...)):
    # extract the structured content of the website
    structured_content = extract_text_with_structure(url)

    all_chunks = []
    # list of metadata for each chunk
    metadata_list = []

    for item in structured_content:
        # text of the content
        text = item["text"]
        chunks = chunk_text(text)

        for chunk in chunks:
            # add the chunk to the list of all chunks
            all_chunks.append(chunk)

            # add the metadata to the list of metadata
            metadata_list.append({
                "html": item["html"],
                "path": item["path"],
                "tag_id": item["tag_id"],
                "tag_class": item["tag_class"],
                "tag_name": item["tag_name"],
                "full_text": text
            })

    # index the chunks
    index_chunks(all_chunks, url_prefix=url, metadata_list=metadata_list)

    print("\n===== DEBUG METADATA BEFORE INDEXING =====")
    # print the metadata of the first chunk for debugging
    print(metadata_list[0])
    print("==========================================\n")

    # return the result
    return {
        "message": f"Indexed {len(all_chunks)} chunks from {url}",
        "total_chunks": len(all_chunks),
        "max_tokens_per_chunk": 500
    }


@app.get("/search")
def search_websites(query: str = Query(...), top_k: int = Query(10, le=50)):
    """Search across all indexed websites"""
    results = semantic_search(query, top_k=top_k)

    return {
        "results_returned": len(results),
        "max_tokens_per_chunk": 500,
        "results": results
    }


@app.delete("/index/clear")
def clear_index():
    """Clear all vectors from the index (useful for re-indexing)"""
    from utils.vector_search import index
    try:
        index.delete(delete_all=True)
        return {"message": "Index cleared successfully. You can now re-index websites."}
    except Exception as e:
        return {"error": str(e)}
