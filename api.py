"""
FastAPI Backend for AI Study Assistant
"""
import os
import shutil
import uvicorn
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from agent import StudyAssistantAgent
from models import StudyRequest, StudyResponse, QuizQuestionResponse
from config import QuizQuestion

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Study Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    global agent
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
    
    # Initialize agent
    try:
        agent = StudyAssistantAgent(openai_key, tavily_key)
        print("✅ Study Assistant Agent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent_initialized": agent is not None}

@app.post("/api/process", response_model=StudyResponse)
async def process_content(request: StudyRequest):
    """Process text, URL, or search query"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if request.input_type == "file":
        raise HTTPException(
            status_code=400, 
            detail="File input not supported in this endpoint. Use /api/process_file"
        )
    
    try:
        result = await agent.run(
            input_type=request.input_type,
            input_data=request.input_data,
            num_questions=request.num_questions,
            difficulty_level=request.difficulty
        )
        return _format_response(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process_file", response_model=StudyResponse)
async def process_file(
    file: UploadFile = File(...),
    num_questions: int = Form(5),
    difficulty: str = Form("mixed")
):
    """Process uploaded file"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process file
        result = await agent.run(
            input_type="file",
            input_data=file_path,
            num_questions=num_questions,
            difficulty_level=difficulty
        )
        
        # Cleanup (optional - keeping for now for debugging/caching potential)
        # os.remove(file_path)
        
        return _format_response(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def _format_response(result: dict) -> StudyResponse:
    """Format agent result into API response"""
    
    # Convert QuizQuestion objects to response models
    quiz_questions = []
    if "quiz_questions" in result:
        for q in result["quiz_questions"]:
            if isinstance(q, QuizQuestion):
                quiz_questions.append(QuizQuestionResponse(
                    question=q.question,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    difficulty=q.difficulty
                ))
            elif isinstance(q, dict):
                 quiz_questions.append(QuizQuestionResponse(**q))
    
    return StudyResponse(
        summary=result.get("summary", ""),
        key_points=result.get("key_points", []),
        quiz=quiz_questions,
        messages=result.get("messages", []),
        error=result.get("error")
    )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
