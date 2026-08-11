from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_match_score(resume_text: str, job_description: str) -> float:
    if not resume_text or not job_description:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    score = round(float(similarity) * 100, 2)
    return score