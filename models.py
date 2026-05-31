from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResumeModel(BaseModel):
    filename: str
    raw_text: str
    skills: str
    projects: str
    job_role: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class UserModel(BaseModel):
    email: str
    resumes: List[ResumeModel] = []

class OutputModel(BaseModel):
    user_email: str
    resume_filename: str
    job_research: str
    resume_summary: str
    cold_email: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class RunRequest(BaseModel):
    user_email: str
    resume_filename: str