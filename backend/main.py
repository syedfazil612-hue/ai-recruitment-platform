from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db, Base
import models, schemas, auth, matching
import pdfplumber
import os
import shutil

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-recruitment-frontend-f32f.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "AI Recruitment Platform Backend is running"}

@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer", "role": db_user.role, "user_id": db_user.id}

@app.post("/jobs", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    new_job = models.Job(
        recruiter_id=job.recruiter_id,
        title=job.title,
        description=job.description
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/jobs", response_model=List[schemas.JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()

@app.post("/upload-resume", response_model=schemas.ResumeResponse)
def upload_resume(candidate_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, f"{candidate_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception as e:
        extracted_text = ""

    new_resume = models.Resume(
        candidate_id=candidate_id,
        file_path=file_path,
        extracted_text=extracted_text
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume

@app.post("/match", response_model=schemas.MatchResponse)
def match_resume_to_job(request: schemas.MatchRequest, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == request.resume_id).first()
    job = db.query(models.Job).filter(models.Job.id == request.job_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    score = matching.get_match_score(resume.extracted_text, job.description)

    return {
        "resume_id": resume.id,
        "job_id": job.id,
        "score": score
    }

@app.post("/apply", response_model=schemas.ApplicationResponse)
def apply_to_job(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.candidate_id == application.candidate_id).order_by(models.Resume.id.desc()).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No resume found for this candidate")

    new_application = models.Application(
        job_id=application.job_id,
        resume_id=resume.id
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@app.get("/jobs/{job_id}/applicants", response_model=List[schemas.ApplicantScore])
def get_applicants_with_scores(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = db.query(models.Application).filter(models.Application.job_id == job_id).all()
    results = []

    for app_row in applications:
        resume = db.query(models.Resume).filter(models.Resume.id == app_row.resume_id).first()
        candidate = db.query(models.User).filter(models.User.id == resume.candidate_id).first()

        score = matching.get_match_score(resume.extracted_text, job.description)

        existing_score = db.query(models.MatchScore).filter(models.MatchScore.application_id == app_row.id).first()
        if existing_score:
            existing_score.score = score
        else:
            db.add(models.MatchScore(application_id=app_row.id, score=score))
        db.commit()

        results.append({
            "application_id": app_row.id,
            "candidate_name": candidate.name,
            "score": score
        })

    return results

@app.post("/generate-questions", response_model=schemas.InterviewQuestionsResponse)
def generate_questions(request: schemas.InterviewQuestionsRequest, db: Session = Depends(get_db)):
    application = db.query(models.Application).filter(models.Application.id == request.application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    resume = db.query(models.Resume).filter(models.Resume.id == application.resume_id).first()
    job = db.query(models.Job).filter(models.Job.id == application.job_id).first()
    candidate = db.query(models.User).filter(models.User.id == resume.candidate_id).first() if resume else None

    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job not found for this application")

    try:
        questions = matching.generate_interview_questions(resume.extracted_text, job.description)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "application_id": application.id,
        "candidate_name": candidate.name if candidate else "Unknown",
        "questions": questions
    }