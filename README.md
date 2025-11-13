<!-- Clone the repository -->
git clone https://github.com/yashpatil02121/domsearch-backend.git

<!-- Navigate to the repository -->
cd domsearch-backend

<!-- Create a virtual environment -->
python -m venv venv
py -3.10 -m venv venv

<!-- Activate the virtual environment -->
venv\Scripts\activate

<!-- Install the dependencies -->
pip install fastapi uvicorn requests beautifulsoup4 pinecone-client pinecone sentence-transformers transformers nltk python-dotenv pydantic
pip install -r requirements.txt

<!-- Set the environment variables -->
<!-- save .env file in the root directory of domsearch-backend with the following content: -->
PINECONE_API_KEY=pcsk_5AiSFQ_4EQX7JiQ5PCWcoTCPDqXmhsnBuB8Ys3o6iSg84hjs6SBSHVmWxrWEJSFJzH6xnR
PINECONE_INDEX_NAME=developer-quickstart-py
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
MAX_TOKENS_PER_CHUNK=500

<!-- Run the application -->
uvicorn main:app --reload
