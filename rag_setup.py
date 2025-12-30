import chromadb
from sentence_transformers import SentenceTransformer
import os

def load_policy_db():
    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create DB client
    client = chromadb.Client()

    # Create vector collection
    db = client.create_collection(name="policy_db")

    # Read policies
    policy_path = os.path.join("data", "policies.txt")
    with open(policy_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    # Store each policy rule
    for i, line in enumerate(lines):
        emb = model.encode([line]).tolist()
        db.add(
            documents=[line],
            embeddings=[emb],
            ids=[str(i)]
        )

    return db, model

def search_policy(db, model, query):
    emb = model.encode([query]).tolist()
    result = db.query(query_embeddings=emb, n_results=1)
    return result['documents'][0][0]
