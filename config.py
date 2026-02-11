"""
AI Study Assistant - LangGraph Agent State and Configuration
"""
from typing import TypedDict, Annotated, List, Optional
from operator import add
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """Structure for a quiz question"""
    question: str = Field(description="The quiz question")
    options: List[str] = Field(description="Multiple choice options")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation for the answer")
    difficulty: str = Field(description="Difficulty level: easy, medium, hard")


class StudyMaterial(BaseModel):
    """Structure for study material"""
    content: str = Field(description="The study material content")
    source: str = Field(description="Source of the material")
    topic: Optional[str] = Field(default=None, description="Topic/subject")


class AgentState(TypedDict):
    """State of the AI Study Assistant Agent"""
    # Input
    input_type: str  # 'file', 'text', 'url', 'search'
    input_data: str  # File path, text content, URL, or search query
    
    # Processing
    raw_content: str
    study_materials: List[StudyMaterial]
    summary: str
    key_points: List[str]
    
    # Quiz Generation
    num_questions: int
    difficulty_level: str  # 'easy', 'medium', 'hard', 'mixed'
    quiz_questions: Annotated[List[QuizQuestion], add]
    
    # Metadata and tracking
    current_step: str
    error: Optional[str]
    mlflow_run_id: Optional[str]
    
    # Messages for conversation
    messages: Annotated[List[str], add]


class Config:
    """Configuration constants"""
    # LLM Settings
    MODEL_NAME = "gpt-4-turbo-preview"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Chunking Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Summary Settings
    MAX_SUMMARY_LENGTH = 500
    
    # Quiz Settings
    DEFAULT_NUM_QUESTIONS = 5
    QUESTION_TYPES = ["multiple_choice", "true_false", "short_answer"]
    
    # MLflow Settings
    EXPERIMENT_NAME = "ai-study-assistant"
    
    # Supported file types
    SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".txt", ".md"]