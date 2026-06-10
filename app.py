import os
import asyncio
import nest_asyncio
nest_asyncio.apply()
import json
import time
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

# region agent log
def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data=None):
    payload = {
        "sessionId": "4008b8",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open("debug-4008b8.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        pass
# endregion

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await ping_db()

@app.post("/upload-resume/{user_email}")
async def upload_resume(user_email: str, file: UploadFile = File(...)):
    # region agent log
    _debug_log("initial", "H2", "app.py:upload_resume:entry", "Upload resume request", {"user_email": user_email, "filename": file.filename})
    # endregion
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    parsed = parse_resume_with_llm(raw_text, llm)
    # region agent log
    _debug_log("initial", "H3", "app.py:upload_resume:parsed", "Resume parse result shape", {"has_skills": "skills" in parsed, "has_projects": "projects" in parsed, "has_job_role": "job_role" in parsed})
    # endregion
    
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

@app.get("/resumes/{user_email}")
async def get_resumes(user_email: str):
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"resumes": user.get("resumes", [])}

@app.post("/run")
async def run_agents(request: RunRequest):
    # region agent log
    _debug_log("initial", "H1", "app.py:run_agents:entry", "Run endpoint invoked", {"user_email": request.user_email, "resume_filename": request.resume_filename})
    # endregion
    user = await users_collection.find_one({"email": request.user_email})
    if not user:
        # region agent log
        _debug_log("initial", "H1", "app.py:run_agents:user_lookup", "User missing", {"user_email": request.user_email})
        # endregion
        raise HTTPException(status_code=404, detail="User not found")
    # region agent log
    _debug_log("initial", "H1", "app.py:run_agents:user_found", "User found", {"resumes_count": len(user.get("resumes", []))})
    # endregion
    
    resume = next(
        (r for r in user["resumes"] if r["filename"] == request.resume_filename),
        None
    )
    if not resume:
        # region agent log
        _debug_log("initial", "H1", "app.py:run_agents:resume_lookup", "Resume missing in user document", {"requested_resume": request.resume_filename})
        # endregion
        raise HTTPException(status_code=404, detail="Resume not found")
    
    tasks = create_tasks(
        job_role=resume["job_role"],
        skills=resume["skills"][:300],
        projects=resume["projects"][:300]
    )
    
    crew = Crew(
        agents=[job_researcher, resume_tailor, cover_letter_writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )
    
    result = await asyncio.to_thread(crew.kickoff)
    # region agent log
    _debug_log("initial", "H4", "app.py:run_agents:kickoff_done", "Crew kickoff completed", {"result_type": str(type(result)), "task0_has_output": bool(tasks[0].output), "task1_has_output": bool(tasks[1].output)})
    # endregion
    
    output = OutputModel(
        user_email=request.user_email,
        resume_filename=request.resume_filename,
        job_research=str(tasks[0].output) if tasks[0].output else "",
        resume_summary=str(tasks[1].output) if tasks[1].output else "",
        cold_email=str(result)
    )
    
    await outputs_collection.insert_one(output.dict())
    # region agent log
    _debug_log("initial", "H5", "app.py:run_agents:output_saved", "Output inserted", {"user_email": request.user_email, "resume_filename": request.resume_filename})
    # endregion
    
    return {
        "job_research": output.job_research,
        "resume_summary": output.resume_summary,
        "cold_email": output.cold_email
    }

@app.get("/outputs/{user_email}")
async def get_outputs(user_email: str):
    outputs = await outputs_collection.find(
        {"user_email": user_email}
    ).to_list(length=10)
    for o in outputs:
        o["_id"] = str(o["_id"])
    return {"outputs": outputs}