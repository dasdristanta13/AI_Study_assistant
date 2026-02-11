"""
LLM Chains for Summarization and Quiz Generation
"""
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.output_parsers import PydanticOutputParser

from config import Config, QuizQuestion


class SummarizationChain:
    """Chain for generating summaries and key points"""
    
    def __init__(self, api_key: str, model_name: str = Config.MODEL_NAME):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.3,  # Lower temperature for more focused summaries
        )
    
    def summarize_content(self, content: str, max_length: int = 500) -> str:
        """Generate a concise summary of the content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational content summarizer. 
            Create a clear, concise summary that captures the main ideas and essential information.
            Focus on key concepts, important facts, and main arguments.
            The summary should be suitable for students studying this material."""),
            ("user", """Summarize the following content in approximately {max_length} words:

{content}

Summary:""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "content": content,
            "max_length": max_length
        })
        
        return response.content
    
    def extract_key_points(self, content: str, num_points: int = 10) -> List[str]:
        """Extract key points from the content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying key learning points from educational content.
            Extract the most important concepts, facts, and ideas that students should remember.
            Each key point should be clear, concise, and self-contained."""),
            ("user", """Extract {num_points} key learning points from the following content.
            Format each point as a clear, concise statement.

Content:
{content}

Provide the key points as a numbered list.""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "content": content,
            "num_points": num_points
        })
        
        # Parse the numbered list
        points = []
        for line in response.content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering and add to list
                point = line.lstrip('0123456789.-•) ').strip()
                if point:
                    points.append(point)
        
        return points[:num_points]


class QuizGenerationChain:
    """Chain for generating quiz questions"""
    
    def __init__(self, api_key: str, model_name: str = Config.MODEL_NAME):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=0.7,
        )
        self.parser = PydanticOutputParser(pydantic_object=QuizQuestion)
    
    def generate_quiz_questions(
        self,
        content: str,
        key_points: List[str],
        num_questions: int = 5,
        difficulty: str = "mixed"
    ) -> List[QuizQuestion]:
        """Generate quiz questions based on content and key points"""
        
        key_points_text = "\n".join([f"- {point}" for point in key_points])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educator creating quiz questions for students.
            Generate high-quality multiple-choice questions that test understanding of the material.
            
            Guidelines:
            - Questions should test comprehension, not just memorization
            - Include 4 options (A, B, C, D) for each question
            - Make distractors (wrong answers) plausible but clearly incorrect
            - Provide clear explanations for correct answers
            - Vary difficulty levels appropriately
            
            {format_instructions}"""),
            ("user", """Based on the following study material and key points, generate {num_questions} quiz questions.
            
Difficulty level: {difficulty}

Key Points:
{key_points}

Content:
{content}

Generate {num_questions} high-quality quiz questions. For each question, provide:
1. The question text
2. Four multiple choice options (A, B, C, D)
3. The correct answer (A, B, C, or D)
4. A clear explanation
5. Difficulty level (easy, medium, or hard)

Return each question in the specified JSON format, one per line.""")
        ])
        
        # Truncate content if too long
        if len(content) > 3000:
            content = content[:3000] + "..."
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "content": content,
            "key_points": key_points_text,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Parse questions from response
        questions = self._parse_questions_from_response(response.content, num_questions)
        
        return questions
    
    def _parse_questions_from_response(self, response: str, expected_count: int) -> List[QuizQuestion]:
        """Parse quiz questions from LLM response"""
        questions = []
        
        # Try to extract JSON objects
        import json
        import re
        
        # Find JSON-like structures
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches[:expected_count]:
            try:
                data = json.loads(match)
                question = QuizQuestion(**data)
                questions.append(question)
            except:
                continue
        
        # If parsing failed, create structured questions manually
        if len(questions) < expected_count:
            questions.extend(self._create_fallback_questions(response, expected_count - len(questions)))
        
        return questions[:expected_count]
    
    def _create_fallback_questions(self, response: str, count: int) -> List[QuizQuestion]:
        """Create fallback questions if parsing fails"""
        fallback = []
        
        for i in range(count):
            fallback.append(QuizQuestion(
                question=f"Question {i+1}: Based on the study material, what is an important concept to understand?",
                options=[
                    "Option A - Review the material for details",
                    "Option B - Refer to key points",
                    "Option C - Study the content carefully",
                    "Option D - All of the above"
                ],
                correct_answer="D",
                explanation="This is a placeholder question. Please review the study material.",
                difficulty="medium"
            ))
        
        return fallback