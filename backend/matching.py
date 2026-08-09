from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the model once when the server starts (small, fast model)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_match_score(resume_text: str, job_description: str) -> float:
    if not resume_text or not job_description:
        return 0.0

    embeddings = model.encode([resume_text, job_description])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    # Convert to a 0-100 score
    score = round(float(similarity) * 100, 2)
    return score
