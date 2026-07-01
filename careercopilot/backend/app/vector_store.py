import os
import json
import logging
import chromadb
from .scoring import get_model

logger = logging.getLogger(__name__)

# Configure local persistent storage path for ChromaDB
CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chroma_db")

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_questions_collection():
    """Get or create the ChromaDB collection for questions."""
    return client.get_or_create_collection(name="interview_questions")

def seed_vector_db():
    """
    Read questions from seed_questions.json, generate embeddings,
    and save them into ChromaDB if the collection is empty.
    """
    collection = get_questions_collection()
    
    # Check if collection is already seeded
    count = collection.count()
    if count > 0:
        logger.info(f"ChromaDB questions collection already seeded with {count} items.")
        return

    # Locate seed questions file
    seed_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_questions.json")
    if not os.path.exists(seed_file_path):
        logger.error(f"Seed questions file not found at: {seed_file_path}")
        return

    logger.info("Seeding ChromaDB with questions from seed_questions.json...")
    try:
        with open(seed_file_path, "r") as f:
            questions = json.load(f)
            
        if not questions:
            logger.warning("Seed questions file is empty.")
            return

        documents = []
        metadatas = []
        ids = []
        
        # Prepare content for batch embedding
        for i, q in enumerate(questions):
            documents.append(q["question"])
            metadatas.append({
                "role": q["role"],
                "skill": q["skill"],
                "difficulty": q["difficulty"],
                "type": q["type"]
            })
            ids.append(f"q_{i}")

        embedding_model = get_model()
        if embedding_model is None:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
        else:
            embeddings = embedding_model.encode(documents, convert_to_tensor=False)
            embeddings_list = [emb.tolist() for emb in embeddings]
            collection.add(
                ids=ids,
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas
            )
        logger.info(f"Successfully seeded {len(questions)} questions into ChromaDB.")
        
    except Exception as e:
        logger.error(f"Error seeding ChromaDB: {str(e)}")

def retrieve_questions(matched_skills: list, missing_skills: list, limit: int = 15) -> list[dict]:
    """
    Query ChromaDB for questions matching matched_skills and missing_skills.
    Ensures representation from both categories, merges, and deduplicates.
    """
    collection = get_questions_collection()
    count = collection.count()
    
    if count == 0:
        # Fallback if DB is empty
        logger.warning("ChromaDB collection is empty. Seeding dynamically...")
        seed_vector_db()
        count = collection.count()
        if count == 0:
            return []

    # If no skills are provided, perform a generic fetch
    if not matched_skills and not missing_skills:
        results = collection.peek(limit=limit)
        return format_chroma_results(results)

    embedding_model = get_model()
    if embedding_model is None:
        results = collection.peek(limit=limit)
        return format_chroma_results(results)

    retrieved = {}

    # Query for matched skills if available
    if matched_skills:
        query_text = " ".join(matched_skills)
        try:
            query_emb = embedding_model.encode([query_text])[0].tolist()
            res = collection.query(
                query_embeddings=[query_emb],
                n_results=min(count, limit)
            )
            for q_id, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
                retrieved[q_id] = {
                    "id": q_id,
                    "question": doc,
                    "role": meta.get("role"),
                    "skill": meta.get("skill"),
                    "difficulty": meta.get("difficulty"),
                    "type": meta.get("type"),
                    "distance": dist
                }
        except Exception as e:
            logger.error(f"Error querying matched skills: {str(e)}")

    # Query for missing skills if available
    if missing_skills:
        query_text = " ".join(missing_skills)
        try:
            query_emb = embedding_model.encode([query_text])[0].tolist()
            # Fetch a bit more to ensure coverage
            res = collection.query(
                query_embeddings=[query_emb],
                n_results=min(count, limit)
            )
            for q_id, doc, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
                # If it's already retrieved, we can update or keep the best distance
                if q_id not in retrieved or dist < retrieved[q_id]["distance"]:
                    retrieved[q_id] = {
                        "id": q_id,
                        "question": doc,
                        "role": meta.get("role"),
                        "skill": meta.get("skill"),
                        "difficulty": meta.get("difficulty"),
                        "type": meta.get("type"),
                        "distance": dist
                    }
        except Exception as e:
            logger.error(f"Error querying missing skills: {str(e)}")

    # Sort merged results by distance (lower distance = closer match)
    sorted_questions = sorted(retrieved.values(), key=lambda x: x["distance"])
    
    # Return up to the specified limit
    return sorted_questions[:limit]

def format_chroma_results(peek_results: dict) -> list[dict]:
    """Helper to format results from Chroma peek or get operations."""
    formatted = []
    ids = peek_results.get("ids", [])
    documents = peek_results.get("documents", [])
    metadatas = peek_results.get("metadatas", [])
    
    for i in range(len(ids)):
        meta = metadatas[i] if i < len(metadatas) else {}
        formatted.append({
            "id": ids[i],
            "question": documents[i] if i < len(documents) else "",
            "role": meta.get("role"),
            "skill": meta.get("skill"),
            "difficulty": meta.get("difficulty"),
            "type": meta.get("type")
        })
    return formatted
