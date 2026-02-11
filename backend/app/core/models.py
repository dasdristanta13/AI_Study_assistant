"""
Pydantic models for API request and response validation
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class StudyRequest(BaseModel):
    """Request model for processing study material"""
    input_type: str = Field(..., description="Type of input: 'file', 'text', 'url', 'search'")
    input_data: str = Field(..., description="The actual input data (text, URL, file path, or search query)")
    num_questions: int = Field(5, ge=1, le=20, description="Number of quiz questions to generate")
    difficulty: str = Field("mixed", description="Difficulty level: 'easy', 'medium', 'hard', 'mixed'")


class QuizOption(BaseModel):
    """Model for a quiz option (just a string usually, but good to be explicit if structure changes)"""
    pass # Currently options are just strings in the main code, so we might not need a complex model yet.
         # But the QuizQuestion in config.py is a Pydantic model. We should likely mirror or reuse that.


class QuizQuestionResponse(BaseModel):
    """Response model for a quiz question"""
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str


class SourceModel(BaseModel):
    title: str
    type: str # "file", "url", "search"
    content: Optional[str] = None

class StudyResponse(BaseModel):
    """Response model for study session"""
    summary: str
    key_points: List[str]
    quiz: List[QuizQuestionResponse]
    sources: List[SourceModel] = []
    
    # We might want to include status messages or errors
    messages: List[str] = []
    error: Optional[str] = None
