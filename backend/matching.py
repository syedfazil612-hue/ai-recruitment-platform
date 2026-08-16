import os
import json
import logging
import random
import re
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
logger = logging.getLogger(__name__)
GEMINI_MAX_RETRIES = 3
GEMINI_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


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
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    req = urllib.request.Request(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_error = None
    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            break
        except urllib.error.HTTPError as e:
            error_body = e.read().decode(errors="replace")
            last_error = f"Gemini API error {e.code}: {error_body}"
            if e.code not in GEMINI_RETRYABLE_STATUS_CODES or attempt == GEMINI_MAX_RETRIES:
                logger.exception("Gemini request failed after %s attempt(s).", attempt)
                raise RuntimeError(last_error) from e
        except urllib.error.URLError as e:
            last_error = f"Could not reach Gemini API: {e}"
            if attempt == GEMINI_MAX_RETRIES:
                logger.exception("Gemini network request failed after %s attempt(s).", attempt)
                raise RuntimeError(last_error) from e

        delay_seconds = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
        logger.warning(
            "Gemini request failed on attempt %s/%s; retrying in %.1f seconds. %s",
            attempt,
            GEMINI_MAX_RETRIES,
            delay_seconds,
            last_error,
        )
        time.sleep(delay_seconds)

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
        if not isinstance(questions, list) or not questions:
            raise ValueError
        return [str(q).strip() for q in questions][:5]
    except (json.JSONDecodeError, ValueError):
        # Fallback: the model didn't return clean single-line JSON (e.g. it
        # pretty-printed the array across multiple lines, or the response
        # got cut off). Strip structural JSON characters and split into
        # individual question lines.
        cleaned = text.strip()
        if cleaned.startswith("["):
            cleaned = cleaned[1:]
        if cleaned.endswith("]"):
            cleaned = cleaned[:-1]

        raw_lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        questions = []
        for line in raw_lines:
            # Drop lines that are pure JSON punctuation (e.g. a lone "[" or "]")
            if re.fullmatch(r"[\[\]{}]*", line):
                continue
            # Strip leading list markers/numbering, then quotes and trailing commas
            line = line.strip("-•").strip()
            line = re.sub(r"^\d+[\.\)]\s*", "", line)
            line = line.strip().rstrip(",").strip()
            line = line.strip('"').strip()
            if line:
                questions.append(line)

        if not questions:
            raise RuntimeError(
                "Gemini returned a response that could not be parsed into questions."
            )
        return questions[:5]
