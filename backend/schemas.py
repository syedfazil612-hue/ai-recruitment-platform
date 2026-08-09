from pydantic import BaseModel, EmailStr

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