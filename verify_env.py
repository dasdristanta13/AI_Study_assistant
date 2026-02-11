import sys
print(f"Python executable: {sys.executable}")
try:
    import langchain
    import langchain_openai
    import langgraph
    import gradio
    import mlflow
    import tavily
    print("✅ All core imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
