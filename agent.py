"""
LangGraph Agent - AI Study Assistant
Main agent workflow with state management
"""
import os
from typing import Dict, Any
from datetime import datetime
import time

from langgraph.graph import StateGraph, END
from langchain.schema import Document

from config import AgentState, Config, StudyMaterial, QuizQuestion
from document_processor import DocumentProcessor, validate_file_path
from web_search import WebSearcher, URLContentExtractor
from llm_chains import SummarizationChain, QuizGenerationChain
from mlflow_tracker import MLflowTracker


class StudyAssistantAgent:
    """LangGraph-based AI Study Assistant Agent"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.tavily_api_key = tavily_api_key
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.web_searcher = WebSearcher(tavily_api_key) if tavily_api_key else None
        self.url_extractor = URLContentExtractor()
        self.summarizer = SummarizationChain(openai_api_key)
        self.quiz_generator = QuizGenerationChain(openai_api_key)
        self.mlflow_tracker = MLflowTracker()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("load_content", self.load_content_node)
        workflow.add_node("process_documents", self.process_documents_node)
        workflow.add_node("generate_summary", self.generate_summary_node)
        workflow.add_node("extract_key_points", self.extract_key_points_node)
        workflow.add_node("generate_quiz", self.generate_quiz_node)
        workflow.add_node("finalize", self.finalize_node)
        
        # Define edges
        workflow.set_entry_point("load_content")
        workflow.add_edge("load_content", "process_documents")
        workflow.add_edge("process_documents", "generate_summary")
        workflow.add_edge("generate_summary", "extract_key_points")
        workflow.add_edge("extract_key_points", "generate_quiz")
        workflow.add_edge("generate_quiz", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def load_content_node(self, state: AgentState) -> AgentState:
        """Node: Load content based on input type"""
        state["current_step"] = "loading_content"
        state["messages"].append(f"Loading content from {state['input_type']}...")
        
        try:
            input_type = state["input_type"]
            input_data = state["input_data"]
            
            if input_type == "file":
                # Validate and load file
                if not validate_file_path(input_data):
                    raise ValueError(f"Invalid file: {input_data}")
                
                raw_content, chunks = self.doc_processor.process_document(input_data)
                state["raw_content"] = raw_content
                state["study_materials"] = [
                    StudyMaterial(
                        content=chunk.page_content,
                        source=chunk.metadata.get("source", input_data),
                        topic=None
                    ) for chunk in chunks
                ]
            
            elif input_type == "text":
                # Process direct text input
                raw_content, chunks = self.doc_processor.process_text(input_data)
                state["raw_content"] = raw_content
                state["study_materials"] = [
                    StudyMaterial(
                        content=chunk.page_content,
                        source="direct_input",
                        topic=None
                    ) for chunk in chunks
                ]
            
            elif input_type == "url":
                # Extract content from URL
                doc = self.url_extractor.extract_from_url(input_data)
                raw_content, chunks = self.doc_processor.process_text(
                    doc.page_content,
                    source=input_data
                )
                state["raw_content"] = raw_content
                state["study_materials"] = [
                    StudyMaterial(
                        content=chunk.page_content,
                        source=input_data,
                        topic=None
                    ) for chunk in chunks
                ]
            
            elif input_type == "search":
                # Perform web search
                if not self.web_searcher:
                    raise ValueError("Web search not available (Tavily API key missing)")
                
                search_results = self.web_searcher.search(input_data, max_results=3)
                combined_content = "\n\n".join([doc.page_content for doc in search_results])
                
                raw_content, chunks = self.doc_processor.process_text(
                    combined_content,
                    source=f"search:{input_data}"
                )
                state["raw_content"] = raw_content
                state["study_materials"] = [
                    StudyMaterial(
                        content=chunk.page_content,
                        source=f"search:{input_data}",
                        topic=input_data
                    ) for chunk in chunks
                ]
            
            else:
                raise ValueError(f"Unknown input type: {input_type}")
            
            state["messages"].append(f"✓ Content loaded: {len(state['raw_content'])} characters")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error loading content: {str(e)}")
        
        return state
    
    def process_documents_node(self, state: AgentState) -> AgentState:
        """Node: Process and prepare documents"""
        state["current_step"] = "processing_documents"
        state["messages"].append("Processing documents...")
        
        try:
            # Documents are already processed in load_content_node
            num_chunks = len(state.get("study_materials", []))
            state["messages"].append(f"✓ Processed into {num_chunks} chunks")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error processing documents: {str(e)}")
        
        return state
    
    def generate_summary_node(self, state: AgentState) -> AgentState:
        """Node: Generate summary of content"""
        state["current_step"] = "generating_summary"
        state["messages"].append("Generating summary...")
        
        try:
            # Combine content from all study materials
            content = "\n\n".join([
                material.content for material in state["study_materials"]
            ])
            
            # Limit content length for summarization
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            # Generate summary
            summary = self.summarizer.summarize_content(
                content,
                max_length=Config.MAX_SUMMARY_LENGTH
            )
            
            state["summary"] = summary
            state["messages"].append(f"✓ Summary generated ({len(summary)} chars)")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error generating summary: {str(e)}")
            state["summary"] = "Summary generation failed."
        
        return state
    
    def extract_key_points_node(self, state: AgentState) -> AgentState:
        """Node: Extract key points from content"""
        state["current_step"] = "extracting_key_points"
        state["messages"].append("Extracting key points...")
        
        try:
            # Combine content from all study materials
            content = "\n\n".join([
                material.content for material in state["study_materials"]
            ])
            
            # Limit content length
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            # Extract key points
            key_points = self.summarizer.extract_key_points(content, num_points=10)
            
            state["key_points"] = key_points
            state["messages"].append(f"✓ Extracted {len(key_points)} key points")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error extracting key points: {str(e)}")
            state["key_points"] = []
        
        return state
    
    def generate_quiz_node(self, state: AgentState) -> AgentState:
        """Node: Generate quiz questions"""
        state["current_step"] = "generating_quiz"
        state["messages"].append("Generating quiz questions...")
        
        try:
            # Prepare content for quiz generation
            content = state.get("summary", state["raw_content"][:3000])
            key_points = state.get("key_points", [])
            num_questions = state.get("num_questions", Config.DEFAULT_NUM_QUESTIONS)
            difficulty = state.get("difficulty_level", "mixed")
            
            # Generate quiz questions
            questions = self.quiz_generator.generate_quiz_questions(
                content=content,
                key_points=key_points,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            state["quiz_questions"] = questions
            state["messages"].append(f"✓ Generated {len(questions)} quiz questions")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error generating quiz: {str(e)}")
            state["quiz_questions"] = []
        
        return state
    
    def finalize_node(self, state: AgentState) -> AgentState:
        """Node: Finalize and prepare output"""
        state["current_step"] = "finalizing"
        state["messages"].append("Finalizing results...")
        
        try:
            state["messages"].append("✓ Study assistant processing complete!")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error finalizing: {str(e)}")
        
        return state
    
    def run(
        self,
        input_type: str,
        input_data: str,
        num_questions: int = 5,
        difficulty_level: str = "mixed"
    ) -> Dict[str, Any]:
        """Run the study assistant agent"""
        
        # Start MLflow run
        run_id = self.mlflow_tracker.start_run()
        start_time = time.time()
        
        # Initialize state
        initial_state = {
            "input_type": input_type,
            "input_data": input_data,
            "raw_content": "",
            "study_materials": [],
            "summary": "",
            "key_points": [],
            "num_questions": num_questions,
            "difficulty_level": difficulty_level,
            "quiz_questions": [],
            "current_step": "initialized",
            "error": None,
            "mlflow_run_id": run_id,
            "messages": []
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log to MLflow
            self.mlflow_tracker.log_study_session(
                input_type=input_type,
                num_questions=num_questions,
                difficulty=difficulty_level,
                processing_time=processing_time,
                summary_length=len(final_state.get("summary", "")),
                num_key_points=len(final_state.get("key_points", [])),
                success=final_state.get("error") is None
            )
            
            # Log artifacts
            self.mlflow_tracker.log_text(
                final_state.get("summary", ""),
                "summary.txt"
            )
            self.mlflow_tracker.log_dict(
                {"key_points": final_state.get("key_points", [])},
                "key_points.json"
            )
            self.mlflow_tracker.log_dict(
                {"questions": [q.dict() for q in final_state.get("quiz_questions", [])]},
                "quiz_questions.json"
            )
            
            # End MLflow run
            self.mlflow_tracker.end_run(status="FINISHED")
            
            return final_state
            
        except Exception as e:
            self.mlflow_tracker.end_run(status="FAILED")
            raise e