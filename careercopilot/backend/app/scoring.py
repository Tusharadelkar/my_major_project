import logging
import os
import re

# Configure logging
logger = logging.getLogger(__name__)

model = None
util = None


def get_model():
    """Load the embedding model lazily so API startup and health checks stay fast."""
    global model, util
    if os.getenv("CAREERCOPILOT_USE_EMBEDDINGS", "0") != "1":
        return None
    if model is None:
        logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
        from sentence_transformers import SentenceTransformer, util as st_util

        model = SentenceTransformer("all-MiniLM-L6-v2")
        util = st_util
        logger.info("SentenceTransformer model loaded successfully.")
    return model


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9+#.]+", text.lower()) if len(token) > 1}


def _keyword_score(resume_text: str, job_description_text: str) -> int:
    resume_tokens = _tokenize(resume_text)
    job_tokens = _tokenize(job_description_text)
    if not resume_tokens or not job_tokens:
        return 0
    overlap = len(resume_tokens & job_tokens)
    return min(100, int((overlap / len(job_tokens)) * 100))

def compute_ats_score(resume_text: str, job_description_text: str) -> int:
    """
    Computes ATS score (0-100) by calculating the cosine similarity
    between the resume text and the job description text.
    """
    if not resume_text or not job_description_text:
        return 0

    try:
        embedding_model = get_model()
        if embedding_model is None:
            return _keyword_score(resume_text, job_description_text)

        embeddings = embedding_model.encode([resume_text, job_description_text], convert_to_tensor=True)
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
        return min(100, int(max(0.0, similarity) * 100))
    except Exception as e:
        logger.error(f"Error computing ATS score: {str(e)}")
        # Default fallback
        return 50

def analyze_skill_gaps(resume_skills: list, job_skills: list, resume_text: str = "") -> tuple[list, list]:
    """
    Compares resume skills against job description skills using keyword and embedding similarity.
    Returns:
        (matched_skills, missing_skills)
    """
    matched_skills = []
    missing_skills = []

    if not job_skills:
        return matched_skills, missing_skills

    # Normalize skills for exact keyword matching
    normalized_resume_skills = [s.strip().lower() for s in resume_skills if s]
    resume_text_lower = resume_text.lower() if resume_text else ""

    # Generate embeddings for skills for semantic matching
    try:
        embedding_model = get_model()
        resume_embeddings = (
            embedding_model.encode(resume_skills, convert_to_tensor=True)
            if embedding_model is not None and resume_skills
            else None
        )
    except Exception as e:
        logger.error(f"Failed to embed resume skills: {str(e)}")
        resume_embeddings = None

    for job_skill in job_skills:
        if not job_skill:
            continue
            
        job_skill_lower = job_skill.strip().lower()

        # 1. Direct Keyword Match: Check exact name in list or if the word appears in resume text
        if (job_skill_lower in normalized_resume_skills) or (resume_text_lower and job_skill_lower in resume_text_lower):
            matched_skills.append(job_skill)
            continue

        # 2. Embedding Similarity Match: If exact keyword match fails, check similarity
        if resume_embeddings is not None and len(resume_skills) > 0:
            try:
                job_embedding = embedding_model.encode(job_skill, convert_to_tensor=True)
                similarities = util.cos_sim(job_embedding, resume_embeddings)[0]
                max_sim = similarities.max().item()

                # Threshold 0.70 represents high semantic similarity
                if max_sim >= 0.70:
                    matched_skills.append(job_skill)
                else:
                    missing_skills.append(job_skill)
            except Exception as e:
                logger.error(f"Error matching embedding for skill '{job_skill}': {str(e)}")
                missing_skills.append(job_skill)
        else:
            missing_skills.append(job_skill)

    return matched_skills, missing_skills
