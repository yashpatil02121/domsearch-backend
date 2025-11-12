from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from utils.html_parser import extract_clean_text, extract_text_with_structure
from utils.chunker import chunk_text
from utils.vector_search import index_chunks, semantic_search

app = FastAPI()

class IndexRequest(BaseModel):
    urls: List[str]

@app.post("/index")
def index_website(url: str = Query(...)):
    """Index a single website for searching with DOM structure"""
    # 1️⃣ Parse HTML with structure
    structured_content = extract_text_with_structure(url)
    
    # 2️⃣ Tokenize and split into 500-token chunks
    all_chunks = []
    metadata_list = []
    
    for item in structured_content:
        text = item['text']
        chunks = chunk_text(text)
        
        for chunk in chunks:
            all_chunks.append(chunk)
            # Store metadata for each chunk
            metadata_list.append({
                'html': item['html'],
                'path': item['path'],
                'tag_id': item['tag_id'],
                'tag_class': item['tag_class'],
                'tag_name': item['tag_name']
            })
    
    total_chunks = len(all_chunks)

    # 3️⃣ Index chunks with metadata
    index_chunks(all_chunks, url_prefix=url, metadata_list=metadata_list)

    return {
        "message": f"Indexed {total_chunks} chunks from {url}",
        "total_chunks": total_chunks,
        "max_tokens_per_chunk": 500
    }

@app.post("/index/bulk")
def index_websites_bulk(request: IndexRequest):
    """Index multiple websites for searching with DOM structure"""
    total_chunks_all = 0
    results = []

    for url in request.urls:
        try:
            # 1️⃣ Parse HTML with structure
            structured_content = extract_text_with_structure(url)
            
            # 2️⃣ Tokenize and split into 500-token chunks
            all_chunks = []
            metadata_list = []
            
            for item in structured_content:
                text = item['text']
                chunks = chunk_text(text)
                
                for chunk in chunks:
                    all_chunks.append(chunk)
                    # Store metadata for each chunk
                    metadata_list.append({
                        'html': item['html'],
                        'path': item['path'],
                        'tag_id': item['tag_id'],
                        'tag_class': item['tag_class'],
                        'tag_name': item['tag_name']
                    })
            
            total_chunks = len(all_chunks)
            total_chunks_all += total_chunks

            # 3️⃣ Index chunks with metadata
            index_chunks(all_chunks, url_prefix=url, metadata_list=metadata_list)

            results.append({
                "url": url,
                "status": "success",
                "chunks_indexed": total_chunks
            })
        except Exception as e:
            results.append({
                "url": url,
                "status": "error",
                "error": str(e)
            })

    return {
        "message": f"Indexed {total_chunks_all} chunks from {len(request.urls)} URLs",
        "total_chunks": total_chunks_all,
        "max_tokens_per_chunk": 500,
        "results": results
    }

@app.get("/search")
def search_websites(query: str = Query(...), top_k: int = Query(10, le=50)):
    """Search across all indexed websites"""
    # Search across all indexed content
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
        # Delete all vectors by namespace (or delete entire index)
        index.delete(delete_all=True)
        return {"message": "Index cleared successfully. You can now re-index websites."}
    except Exception as e:
        return {"error": str(e)}
