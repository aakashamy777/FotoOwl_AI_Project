import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()

DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "models/gemini-embedding-001"

def get_embeddings():
    """Return the configured Google Generative AI embeddings instance."""
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

def ingest_all():
    """Ingest both style guides and remotion snippets into separate Chroma collections."""
    embeddings = get_embeddings()
    print("Ingestion skeleton ready.")

def get_retriever(collection_name: str, k: int = 3):
    """Return a retriever for the specified Chroma collection."""
    db = Chroma(collection_name=collection_name, persist_directory=DB_DIR, embedding_function=get_embeddings())
    return db.as_retriever(search_kwargs={"k": k})

if __name__ == "__main__":
    ingest_all()
