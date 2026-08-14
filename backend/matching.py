import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()


def get_match_score(resume_text: str, job_description: str) -> float:
    if not resume_text or not job_description:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    score = round(float(similarity) * 100, 2)
    return score


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)


def generate_interview_questions(resume_text: str, job_description: str) -> list[str]:
    """
    Calls the Gemini API to generate 5 tailored interview questions
    based on a candidate's resume text and a job description.
    Returns a list of question strings. Raises RuntimeError on failure.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured on the server.")

    prompt = (
        "You are an experienced technical recruiter. Based on the candidate's resume "
        "and the job description below, write exactly 5 targeted interview questions "
        "that probe the candidate's fit for this specific role. Mix technical and "
        "behavioural questions. Return ONLY a JSON array of 5 strings, no other text, "
        "no markdown formatting, no code fences.\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"CANDIDATE RESUME:\n{resume_text[:6000]}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800},
    }

    req = urllib.request.Request(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Gemini API error {e.code}: {e.read().decode()}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach Gemini API: {e}")

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError("Unexpected response format from Gemini API.")

    # Strip markdown code fences if the model added them despite instructions
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        questions = json.loads(text)
        if not isinstance(questions, list):
            raise ValueError
        return [str(q) for q in questions][:5]
    except (json.JSONDecodeError, ValueError):
        # Fallback: split by lines if the model didn't return clean JSON
        lines = [
            line.strip("-•1234567890. ").strip()
            for line in text.split("\n")
            if line.strip()
        ]
        return lines[:5]