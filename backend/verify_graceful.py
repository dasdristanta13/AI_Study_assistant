import asyncio
import os
from dotenv import load_dotenv
from app.agent.agent import StudyAssistantAgent

# Load env but force bad keys for testing
os.environ["OPENAI_API_KEY"] = "sk-invalid-key-for-testing"
os.environ["TAVILY_API_KEY"] = "tvly-invalid-key"

async def test_graceful_failure():
    print("🤖 Initializing agent with INVALID keys...")
    agent = StudyAssistantAgent("sk-invalid-key", "tvly-invalid-key")
    
    if agent.init_error:
        print(f"✓ Agent captured init error: {agent.init_error}")
    else:
        print("❓ Agent initialized without error (Components might be lazy loaded)")
        
    print("\n🏃 Running agent...")
    result = await agent.run(
        input_type="text",
        input_data="Test content",
        num_questions=1
    )
    
    print("\n📊 Result:")
    print(f"Error Field: {result.get('error')}")
    print(f"Messages: {result.get('messages')}")
    
    if result.get("error"):
        print("\n✅ SUCCESS: Agent returned error gracefully instead of crashing.")
    else:
        print("\n❌ FAILURE: Agent did not report error.")

if __name__ == "__main__":
    asyncio.run(test_graceful_failure())
