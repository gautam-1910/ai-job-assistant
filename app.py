import os
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from crewai import Crew, Process
from database import users_collection, outputs_collection, ping_db
from models import UserModel, ResumeModel, OutputModel, RunRequest
from resume_parser import extract_text_from_pdf, parse_resume_with_llm
from agents import job_researcher, resume_tailor, cover_letter_writer, llm
from tasks import create_tasks

load_dotenv()

app = FastAPI(title="AI Job Assistant")

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await ping_db()

# Upload resume endpoint
@app.post("/upload-resume/{user_email}")
async def upload_resume(user_email: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    parsed = parse_resume_with_llm(raw_text, llm)
    
    resume = ResumeModel(
        filename=file.filename,
        raw_text=raw_text,
        skills=parsed["skills"],
        projects=parsed["projects"],
        job_role=parsed["job_role"]
    )
    
    await users_collection.update_one(
        {"email": user_email},
        {"$push": {"resumes": resume.dict()},
         "$setOnInsert": {"email": user_email}},
        upsert=True
    )
    
    return {"message": "Resume uploaded successfully", "parsed": parsed}

# Get all resumes for a user
@app.get("/resumes/{user_email}")
async def get_resumes(user_email: str):
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"resumes": user.get("resumes", [])}

# Run agents
@app.post("/run")
async def run_agents(request: RunRequest):
    user = await users_collection.find_one({"email": request.user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resume = next(
        (r for r in user["resumes"] if r["filename"] == request.resume_filename),
        None
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    tasks = create_tasks(
        job_role=resume["job_role"],
        skills=resume["skills"],
        projects=resume["projects"]
    )
    
    crew = Crew(
        agents=[job_researcher, resume_tailor, cover_letter_writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    
    result = await asyncio.to_thread(crew.kickoff)
    
    output = OutputModel(
        user_email=request.user_email,
        resume_filename=request.resume_filename,
        job_research=str(tasks[0].output) if tasks[0].output else "",
        resume_summary=str(tasks[1].output) if tasks[1].output else "",
        cold_email=str(result)
    )
    
    await outputs_collection.insert_one(output.dict())
    
    return {
        "job_research": output.job_research,
        "resume_summary": output.resume_summary,
        "cold_email": output.cold_email
    }

# Get previous outputs for a user
@app.get("/outputs/{user_email}")
async def get_outputs(user_email: str):
    outputs = await outputs_collection.find(
        {"user_email": user_email}
    ).to_list(length=10)
    for o in outputs:
        o["_id"] = str(o["_id"])
    return {"outputs": outputs}