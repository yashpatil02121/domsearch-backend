from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI, Query
from utils.html_parser import extract_clean_text
from utils.chunker import chunk_text
from utils.vector_search import index_chunks, semantic_search

app = FastAPI()

@app.get("/search")
def search_website(url: str = Query(...), query: str = Query(...)):
    # Step 1: Get and clean HTML text
    text = extract_clean_text(url)

    # Step 2: Split into chunks
    chunks = chunk_text(text)

    # Step 3: Index chunks
    index_chunks(chunks)

    # Step 4: Search for query
    results = semantic_search(query)

    return {"results": results}
