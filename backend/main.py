from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db, Base
import models, schemas, auth
import pdfplumber
import os
import shutil

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
    return {"access_token": token, "token_type": "bearer", "role": db_user.role}

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