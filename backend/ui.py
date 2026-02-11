"""
Gradio UI for AI Study Assistant
Simple web interface for the study assistant
"""
import gradio as gr
import os
from typing import Tuple, List
from dotenv import load_dotenv

from app.agent.agent import StudyAssistantAgent
from app.core.config import QuizQuestion

# Load environment variables
load_dotenv()


class StudyAssistantUI:
    """Gradio-based UI for the study assistant"""
    
    def __init__(self):
        self.agent = None
        self.last_result = None
    
    def initialize_agent(
        self,
        openai_key: str,
        tavily_key: str
    ) -> str:
        """Initialize the agent with API keys"""
        try:
            if not openai_key:
                return "❌ Please provide OpenAI API key"
            
            self.agent = StudyAssistantAgent(
                openai_api_key=openai_key,
                tavily_api_key=tavily_key if tavily_key else None
            )
            return "✅ Agent initialized successfully!"
        except Exception as e:
            return f"❌ Error initializing agent: {str(e)}"
    
    def process_file(
        self,
        file_path: str,
        num_questions: int,
        difficulty: str,
        openai_key: str,
        tavily_key: str
    ) -> Tuple[str, str, str, str]:
        """Process uploaded file"""
        
        # Initialize agent if needed
        if self.agent is None:
            init_msg = self.initialize_agent(openai_key, tavily_key)
            if "Error" in init_msg:
                return init_msg, "", "", ""
        
        try:
            # Run agent
            result = self.agent.run(
                input_type="file",
                input_data=file_path,
                num_questions=num_questions,
                difficulty_level=difficulty
            )
            
            self.last_result = result
            
            # Format outputs
            status = self._format_status(result)
            summary = self._format_summary(result)
            key_points = self._format_key_points(result)
            quiz = self._format_quiz(result)
            
            return status, summary, key_points, quiz
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def process_text(
        self,
        text_input: str,
        num_questions: int,
        difficulty: str,
        openai_key: str,
        tavily_key: str
    ) -> Tuple[str, str, str, str]:
        """Process text input"""
        
        # Initialize agent if needed
        if self.agent is None:
            init_msg = self.initialize_agent(openai_key, tavily_key)
            if "Error" in init_msg:
                return init_msg, "", "", ""
        
        try:
            # Run agent
            result = self.agent.run(
                input_type="text",
                input_data=text_input,
                num_questions=num_questions,
                difficulty_level=difficulty
            )
            
            self.last_result = result
            
            # Format outputs
            status = self._format_status(result)
            summary = self._format_summary(result)
            key_points = self._format_key_points(result)
            quiz = self._format_quiz(result)
            
            return status, summary, key_points, quiz
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def process_url(
        self,
        url: str,
        num_questions: int,
        difficulty: str,
        openai_key: str,
        tavily_key: str
    ) -> Tuple[str, str, str, str]:
        """Process URL input"""
        
        # Initialize agent if needed
        if self.agent is None:
            init_msg = self.initialize_agent(openai_key, tavily_key)
            if "Error" in init_msg:
                return init_msg, "", "", ""
        
        try:
            # Run agent
            result = self.agent.run(
                input_type="url",
                input_data=url,
                num_questions=num_questions,
                difficulty_level=difficulty
            )
            
            self.last_result = result
            
            # Format outputs
            status = self._format_status(result)
            summary = self._format_summary(result)
            key_points = self._format_key_points(result)
            quiz = self._format_quiz(result)
            
            return status, summary, key_points, quiz
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def process_search(
        self,
        search_query: str,
        num_questions: int,
        difficulty: str,
        openai_key: str,
        tavily_key: str
    ) -> Tuple[str, str, str, str]:
        """Process web search"""
        
        # Initialize agent if needed
        if self.agent is None:
            init_msg = self.initialize_agent(openai_key, tavily_key)
            if "Error" in init_msg:
                return init_msg, "", "", ""
        
        if not tavily_key:
            return "❌ Tavily API key required for web search", "", "", ""
        
        try:
            # Run agent
            result = self.agent.run(
                input_type="search",
                input_data=search_query,
                num_questions=num_questions,
                difficulty_level=difficulty
            )
            
            self.last_result = result
            
            # Format outputs
            status = self._format_status(result)
            summary = self._format_summary(result)
            key_points = self._format_key_points(result)
            quiz = self._format_quiz(result)
            
            return status, summary, key_points, quiz
            
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", ""
    
    def _format_status(self, result: dict) -> str:
        """Format status message"""
        messages = result.get("messages", [])
        error = result.get("error")
        
        output = "### Processing Log\n\n"
        for msg in messages:
            output += f"- {msg}\n"
        
        if error:
            output += f"\n**Error:** {error}\n"
        
        return output
    
    def _format_summary(self, result: dict) -> str:
        """Format summary output"""
        summary = result.get("summary", "")
        
        if not summary:
            return "No summary generated."
        
        output = "## 📝 Summary\n\n"
        output += summary
        
        return output
    
    def _format_key_points(self, result: dict) -> str:
        """Format key points output"""
        key_points = result.get("key_points", [])
        
        if not key_points:
            return "No key points extracted."
        
        output = "## 🎯 Key Points\n\n"
        for i, point in enumerate(key_points, 1):
            output += f"{i}. {point}\n\n"
        
        return output
    
    def _format_quiz(self, result: dict) -> str:
        """Format quiz output"""
        questions = result.get("quiz_questions", [])
        
        if not questions:
            return "No quiz questions generated."
        
        output = "## 📚 Quiz Questions\n\n"
        
        for i, q in enumerate(questions, 1):
            output += f"### Question {i}\n\n"
            output += f"**{q.question}**\n\n"
            
            for j, option in enumerate(q.options):
                output += f"{chr(65+j)}. {option}\n"
            
            output += f"\n**Correct Answer:** {q.correct_answer}\n"
            output += f"**Explanation:** {q.explanation}\n"
            output += f"**Difficulty:** {q.difficulty}\n\n"
            output += "---\n\n"
        
        return output
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        with gr.Blocks(title="AI Study Assistant", theme=gr.themes.Soft()) as interface:
            gr.Markdown(
                """
                # 🎓 AI Study Assistant
                
                Transform study materials into summaries and quizzes using LangGraph and LLMs.
                
                **Features:**
                - 📄 Upload documents (PDF, DOCX, TXT, MD)
                - ✍️ Paste text directly
                - 🔗 Extract from URLs
                - 🔍 Search the web for topics
                - 📝 Generate summaries and key points
                - 📚 Create custom quizzes
                """
            )
            
            # API Keys Section
            with gr.Accordion("🔑 API Configuration", open=False):
                openai_key = gr.Textbox(
                    label="OpenAI API Key",
                    type="password",
                    placeholder="sk-...",
                    value=os.getenv("OPENAI_API_KEY", "")
                )
                tavily_key = gr.Textbox(
                    label="Tavily API Key (optional - for web search)",
                    type="password",
                    placeholder="tvly-...",
                    value=os.getenv("TAVILY_API_KEY", "")
                )
            
            # Common Settings
            with gr.Row():
                num_questions = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Number of Quiz Questions"
                )
                difficulty = gr.Radio(
                    choices=["easy", "medium", "hard", "mixed"],
                    value="mixed",
                    label="Difficulty Level"
                )
            
            # Input Tabs
            with gr.Tabs():
                # File Upload Tab
                with gr.Tab("📄 Upload File"):
                    file_input = gr.File(
                        label="Upload Document (PDF, DOCX, TXT, MD)",
                        file_types=[".pdf", ".docx", ".txt", ".md"]
                    )
                    file_button = gr.Button("Process File", variant="primary")
                
                # Text Input Tab
                with gr.Tab("✍️ Paste Text"):
                    text_input = gr.Textbox(
                        label="Study Material",
                        placeholder="Paste your study material here...",
                        lines=10
                    )
                    text_button = gr.Button("Process Text", variant="primary")
                
                # URL Tab
                with gr.Tab("🔗 From URL"):
                    url_input = gr.Textbox(
                        label="URL",
                        placeholder="https://example.com/article"
                    )
                    url_button = gr.Button("Process URL", variant="primary")
                
                # Web Search Tab
                with gr.Tab("🔍 Web Search"):
                    search_input = gr.Textbox(
                        label="Search Query",
                        placeholder="e.g., 'photosynthesis process'"
                    )
                    search_button = gr.Button("Search and Process", variant="primary")
            
            # Output Section
            gr.Markdown("## 📊 Results")
            
            with gr.Tabs():
                with gr.Tab("📝 Summary"):
                    summary_output = gr.Markdown()
                
                with gr.Tab("🎯 Key Points"):
                    key_points_output = gr.Markdown()
                
                with gr.Tab("📚 Quiz"):
                    quiz_output = gr.Markdown()
                
                with gr.Tab("ℹ️ Status"):
                    status_output = gr.Markdown()
            
            # Event Handlers
            file_button.click(
                fn=self.process_file,
                inputs=[file_input, num_questions, difficulty, openai_key, tavily_key],
                outputs=[status_output, summary_output, key_points_output, quiz_output]
            )
            
            text_button.click(
                fn=self.process_text,
                inputs=[text_input, num_questions, difficulty, openai_key, tavily_key],
                outputs=[status_output, summary_output, key_points_output, quiz_output]
            )
            
            url_button.click(
                fn=self.process_url,
                inputs=[url_input, num_questions, difficulty, openai_key, tavily_key],
                outputs=[status_output, summary_output, key_points_output, quiz_output]
            )
            
            search_button.click(
                fn=self.process_search,
                inputs=[search_input, num_questions, difficulty, openai_key, tavily_key],
                outputs=[status_output, summary_output, key_points_output, quiz_output]
            )
            
            # Footer
            gr.Markdown(
                """
                ---
                **Tips:**
                - For best results, provide focused study material
                - Use web search for current topics

                """
            )
        
        return interface


def launch_ui(share: bool = False, server_port: int = 7860):
    """Launch the Gradio UI"""
    ui = StudyAssistantUI()
    interface = ui.create_interface()
    interface.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    launch_ui()