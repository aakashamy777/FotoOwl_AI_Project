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

    # 1. Ingest style guides
    style_docs = []
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("##", "section")])
    for f in glob.glob("rag/style_guides/*.md"):
        style_name = Path(f).stem
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
        chunks = splitter.split_text(content)
        for chunk in chunks:
            chunk.metadata["style"] = style_name
            style_docs.append(chunk)

    db_style = Chroma(collection_name="style_guides", persist_directory=DB_DIR, embedding_function=embeddings)
    db_style.delete_collection()
    db_style = Chroma(collection_name="style_guides", persist_directory=DB_DIR, embedding_function=embeddings)
    if style_docs:
        db_style.add_documents(style_docs)

    print("Ingestion summary:")
    print(f"Style guides chunks: {len(style_docs)}")

def get_retriever(collection_name: str, k: int = 3):
    """Return a retriever for the specified Chroma collection."""
    db = Chroma(collection_name=collection_name, persist_directory=DB_DIR, embedding_function=get_embeddings())
    return db.as_retriever(search_kwargs={"k": k})

if __name__ == "__main__":
    ingest_all()
