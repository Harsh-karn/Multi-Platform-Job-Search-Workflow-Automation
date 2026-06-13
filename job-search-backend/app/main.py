from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from app.parsers.resume_parser import parse_resume
from app.models import ResumeProfile
from app.tasks import process_job_search, celery_app
from celery.result import AsyncResult

app = FastAPI(title="Job Search Automation API")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Job Search API is running."}

@app.post("/search")
async def start_search(file: UploadFile):
    if not file.filename.endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, or TXT allowed.")
        
    session_id = str(uuid.uuid4())
    
    # Read resume text
    # In a real app, you'd use PyPDF2 for PDF or python-docx for DOCX
    # For now, we assume simple text or basic extraction
    try:
        content = await file.read()
        # Attempt to decode as text for simplicity
        resume_text = content.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")
        
    try:
        # 1. Parse resume using Gemini
        profile_dict = parse_resume(resume_text)
        
        # Dispatch Celery task
        task = process_job_search.delay(session_id, profile_dict)
        
        return {
            "session_id": session_id,
            "task_id": task.id,
            "status": "processing",
            "profile": profile_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"status": "processing"}
    elif task_result.state != 'FAILURE':
        result = task_result.result
        return result
    else:
        return {"status": "error", "detail": str(task_result.info)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
