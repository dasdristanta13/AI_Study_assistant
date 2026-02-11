"""
AI Study Assistant - Main Entry Point
"""
import os
import argparse
from dotenv import load_dotenv

from ui import launch_ui
from agent import StudyAssistantAgent


def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Study Assistant")
    parser.add_argument(
        "--mode",
        choices=["ui", "cli"],
        default="ui",
        help="Run mode: ui (Gradio interface) or cli (command line)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio share link"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port for Gradio UI (default: 7860)"
    )
    
    # CLI-specific arguments
    parser.add_argument(
        "--input-type",
        choices=["file", "text", "url", "search"],
        help="Type of input (for CLI mode)"
    )
    parser.add_argument(
        "--input-data",
        help="Input data: file path, text, URL, or search query (for CLI mode)"
    )
    parser.add_argument(
        "--num-questions",
        type=int,
        default=5,
        help="Number of quiz questions to generate"
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "mixed"],
        default="mixed",
        help="Difficulty level for quiz questions"
    )
    
    args = parser.parse_args()
    
    if args.mode == "ui":
        print("🎓 Launching AI Study Assistant UI...")
        print(f"📍 Access the interface at: http://localhost:{args.port}")
        if args.share:
            print("🌐 Public share link will be generated...")

        print("=" * 60)
        
        launch_ui(share=args.share, server_port=args.port)
    
    elif args.mode == "cli":
        if not args.input_type or not args.input_data:
            print("❌ Error: --input-type and --input-data required for CLI mode")
            return
        
        # Get API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not openai_key:
            print("❌ Error: OPENAI_API_KEY environment variable not set")
            return
        
        print("🎓 AI Study Assistant - CLI Mode")
        print("=" * 60)
        
        # Initialize agent
        agent = StudyAssistantAgent(
            openai_api_key=openai_key,
            tavily_api_key=tavily_key
        )
        
        # Run agent
        print(f"📚 Processing {args.input_type}: {args.input_data[:100]}...")
        
        result = agent.run(
            input_type=args.input_type,
            input_data=args.input_data,
            num_questions=args.num_questions,
            difficulty_level=args.difficulty
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📝 SUMMARY")
        print("=" * 60)
        print(result.get("summary", "No summary generated"))
        
        print("\n" + "=" * 60)
        print("🎯 KEY POINTS")
        print("=" * 60)
        for i, point in enumerate(result.get("key_points", []), 1):
            print(f"{i}. {point}")
        
        print("\n" + "=" * 60)
        print("📚 QUIZ QUESTIONS")
        print("=" * 60)
        for i, q in enumerate(result.get("quiz_questions", []), 1):
            print(f"\nQuestion {i}: {q.question}")
            for j, option in enumerate(q.options):
                print(f"  {chr(65+j)}. {option}")
            print(f"  Correct: {q.correct_answer}")
            print(f"  Explanation: {q.explanation}")
            print(f"  Difficulty: {q.difficulty}")
        
        print("\n" + "=" * 60)
        print(f"✅ Processing complete!")



if __name__ == "__main__":
    main()