from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    recruiter_id: int
    title: str
    description: str

class JobResponse(BaseModel):
    id: int
    recruiter_id: int
    title: str
    description: str

    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    file_path: str
    extracted_text: Optional[str] = None

    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    resume_id: int
    job_id: int

class MatchResponse(BaseModel):
    resume_id: int
    job_id: int
    score: float

class ApplicationCreate(BaseModel):
    job_id: int
    candidate_id: int

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    resume_id: int

    class Config:
        from_attributes = True

class ApplicantScore(BaseModel):
    application_id: int
    candidate_name: str
    score: float

class InterviewQuestionsRequest(BaseModel):
    application_id: int

class InterviewQuestionsResponse(BaseModel):
    application_id: int
    candidate_name: str
    questions: List[str]