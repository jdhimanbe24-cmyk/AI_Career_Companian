import os
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_collection(
    name="career_knowledge"
)

def retrieve_context(query, role, n_results=3):
    query_embedding = embedding_model.encode(
        query
    ).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where= {
            "$or": [
                {
                    "role" : role
                },
                {
                    "role" : "GENERAL"
                }
            ]
        }
    )
    
    documents = results.get(
        "documents",
        [[]]
    )[0]
    
    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]
    
    return documents, metadatas
