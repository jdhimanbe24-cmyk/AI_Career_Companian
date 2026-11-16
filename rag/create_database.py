import os
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_BASE = os.path.join(
    BASE_DIR,
    "knowledge_base"
)
CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path = CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="career_knowledge"
)

ROLE_MAPPING = {
    "ai_ml_engineer.txt": "AI/ML Engineer",
    "software_engineer.txt": "Software Engineer",
    "data_scientist.txt": "Data Scientist",
    "web_developer.txt" : "Web Developer",
    "resume_guidelines.txt" : "GENERAL"
}

for filename in os.listdir(KNOWLEDGE_BASE):
    if not filename.endswith(".txt"):
        continue
    
    filepath = os.path.join(
        KNOWLEDGE_BASE,
        filename
    )
    
    with open(
        filepath,
        "r",
        encoding = "utf-8"
    ) as file:
        text = file.read()
        
    chunks = [
        text[i:i + 1000]
        for i in range(0,len(text), 1000)
    ]
    
    role = ROLE_MAPPING.get(
        filename,
        "GENERAL"
    )
    
    
    for index, chunk in enumerate(chunks):
        embedding = embedding_model.encode(
            chunk
        ).tolist()
        
        collection.upsert(
            ids=[
                f"{filename}_{index}"
            ],
            
            documents=[
                chunk
            ],
            
            embeddings=[
                embedding
            ],
            
            metadatas=[
                {
                    "source": filename,
                    "role" : role
                }
            ]
        )
print("Knowledge base successfully added to ChromaDB.")
        
print(
    "Total documents: ",
    collection.count()
)