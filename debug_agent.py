import asyncio
import os
from dotenv import load_dotenv
from agent import StudyAssistantAgent

load_dotenv()

async def debug():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Error: OPENAI_API_KEY not set")
        return

    agent = StudyAssistantAgent(openai_key)
    print("Agent initialized.")
    
    try:
        result = await agent.run(
            input_type="text",
            input_data="Artificial Intelligence is a field of computer science.",
            num_questions=1
        )
        print("Summary:", result.get("summary"))
        print("Error:", result.get("error"))
        print("Messages:", result.get("messages"))
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug())
