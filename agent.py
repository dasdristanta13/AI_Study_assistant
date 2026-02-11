"""
LangGraph Agent - AI Study Assistant
Main agent workflow with state management
"""
import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import time

from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from config import AgentState, Config, StudyMaterial, QuizQuestion
from document_processor import DocumentProcessor, validate_file_path
from web_search import WebSearcher, URLContentExtractor
from llm_chains import SummarizationChain, QuizGenerationChain
from tracing import TracingManager


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
        
        # Initialize tracing
        self.tracing_manager = TracingManager()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("load_content", self.load_content_node)
        workflow.add_node("process_documents", self.process_documents_node)
        workflow.add_node("analyze_content", self.analyze_content_node)
        workflow.add_node("generate_quiz", self.generate_quiz_node)
        workflow.add_node("finalize", self.finalize_node)
        
        # Define edges
        workflow.set_entry_point("load_content")
        workflow.add_edge("load_content", "process_documents")
        workflow.add_edge("process_documents", "analyze_content")
        workflow.add_edge("analyze_content", "generate_quiz")
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
    
    async def analyze_content_node(self, state: AgentState) -> AgentState:
        """Node: Analyze content (Summary + Key Points) in parallel"""
        state["current_step"] = "analyzing_content"
        state["messages"].append("Generating summary and extracting key points...")
        
        try:
            # Combine content from all study materials
            content = "\n\n".join([
                material.content for material in state["study_materials"]
            ])
            
            # Limit content length
            if len(content) > 8000:
                content = content[:8000] + "..."
            
            # Define tasks
            summary_task = self.summarizer.summarize_content(
                content,
                max_length=Config.MAX_SUMMARY_LENGTH
            )
            
            key_points_task = self.summarizer.extract_key_points(
                content,
                num_points=10
            )
            
            # Run in parallel
            summary, key_points = await asyncio.gather(summary_task, key_points_task)
            
            state["summary"] = summary
            state["key_points"] = key_points
            state["messages"].append(f"✓ Analysis complete: Summary ({len(summary)} chars) & {len(key_points)} Key Points")
            
        except Exception as e:
            state["error"] = str(e)
            state["messages"].append(f"✗ Error analyzing content: {str(e)}")
            state["summary"] = "Summary generation failed."
            state["key_points"] = []
        
        return state
    
    async def generate_quiz_node(self, state: AgentState) -> AgentState:
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
            questions = await self.quiz_generator.generate_quiz_questions(
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
    
    async def run(
        self,
        input_type: str,
        input_data: str,
        num_questions: int = 5,
        difficulty_level: str = "mixed"
    ) -> Dict[str, Any]:
        """Run the study assistant agent (Async)"""
        
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
            "messages": []
        }
        
        try:
            # Get tracing callbacks
            callbacks = self.tracing_manager.get_callbacks()
            
            # Run the graph with callbacks (async)
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"callbacks": callbacks} if callbacks else None
            )
            
            # Flush traces if needed
            self.tracing_manager.flush()
            
            return final_state
            
        except Exception as e:
            raise e