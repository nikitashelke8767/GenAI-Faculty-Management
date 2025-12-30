import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load policies text
policy_path = os.path.join(BASE_DIR, "data", "policies.txt")
loader = TextLoader(policy_path)
documents = loader.load()

# Split documents
splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
docs = splitter.split_documents(documents)

# Create embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create ChromaDB
vector_db = Chroma.from_documents(
    docs,
    embedding_model,
    persist_directory=os.path.join(BASE_DIR, "chroma_db")
)

vector_db.persist()

print("✅ Vector database created successfully")
