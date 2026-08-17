# TalentMatch AI — Smart Recruitment Platform

An AI-powered full-stack recruitment platform that connects recruiters with candidates. Recruiters post job openings and review applicants ranked by an automated resume-to-job match score; candidates upload a resume once and apply to any listed role. A built-in LLM feature generates tailored interview questions for each applicant.

## Features

- **Role-based accounts** — separate recruiter and candidate dashboards
- **Resume upload & parsing** — PDF resumes are parsed and stored as searchable text
- **AI match scoring** — TF-IDF + cosine similarity scores each applicant against a job description
- **AI-generated interview questions** — Google Gemini generates five tailored questions per applicant, based on their resume and the job description
- **Applicant tracking** — recruiters view all applicants for a job, ranked by match score

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python), SQLAlchemy ORM |
| Database | PostgreSQL |
| Frontend | React (Vite), Axios, React Router |
| Auth | JWT (python-jose), bcrypt password hashing |
| NLP / Matching | scikit-learn (TF-IDF + cosine similarity) |
| LLM | Google Gemini API |
| PDF Parsing | pdfplumber |
| Deployment | Docker (backend), Render.com (backend + frontend) |

## Project Structure

```
ai-recruitment-platform/
├── backend/          # FastAPI application, models, matching & LLM logic
└── frontend/          # React (Vite) client
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Create a `.env` file in `backend/` with:

```
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/recruitment_db
GEMINI_API_KEY=your_gemini_api_key
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register a recruiter or candidate |
| POST | `/login` | Authenticate and receive a JWT |
| POST | `/jobs` | Recruiter creates a job posting |
| GET | `/jobs` | List all job postings |
| POST | `/upload-resume` | Candidate uploads a resume (PDF) |
| POST | `/apply` | Candidate applies to a job |
| GET | `/jobs/{job_id}/applicants` | Recruiter views applicants with match scores |
| POST | `/generate-questions` | Generate AI interview questions for an applicant |

## Notes on Match Scoring

Match scores are computed with TF-IDF (term frequency–inverse document frequency) vectorization and cosine similarity. This method measures keyword overlap rather than semantic meaning, so absolute scores are typically low (single-digit to low-teens percentages) even for strong candidate–job fits. Scores are most useful for ranking candidates against one another for the same job rather than as an absolute quality percentage.

## License

This project was built as an academic final-year project (B.E. AIML).
