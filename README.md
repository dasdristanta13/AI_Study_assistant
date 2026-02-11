# 🎓 AI Study Assistant

A LangGraph-based agentic system that helps students digest study materials and generate personalized quizzes using LLMs, MLflow tracking, and web search capabilities.

## 🌟 Features

- **Multi-Input Support**: 
  - 📄 Upload documents (PDF, DOCX, TXT, MD)
  - ✍️ Paste text directly
  - 🔗 Extract content from URLs
  - 🔍 Search the web for topics (using Tavily)

- **Intelligent Processing**:
  - 📝 Generate concise summaries
  - 🎯 Extract key learning points
  - 📚 Create custom quiz questions with explanations
  - 🎲 Adjustable difficulty levels (easy, medium, hard, mixed)

- **Advanced Features**:
  - 🤖 LangGraph agent orchestration
  - 📊 MLflow experiment tracking
  - 🌐 Web search integration (Tavily/Firecrawl)
  - 🎨 User-friendly Gradio UI
  - 💻 CLI mode for automation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Gradio Web UI / CLI                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Agent (agent.py)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  load_content → process_docs → generate_summary      │  │
│  │       ↓              ↓              ↓                 │  │
│  │  extract_key_points → generate_quiz → finalize       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Component Layer                             │
│  • DocumentProcessor   • WebSearcher                         │
│  • SummarizationChain  • QuizGenerationChain                │
│  • MLflowTracker       • URLContentExtractor                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services                               │
│  • OpenAI GPT-4  • Tavily Search  • Firecrawl (optional)    │
│  • MLflow Tracking Server                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- OpenAI API key (required)
- Tavily API key (optional, for web search)
- Firecrawl API key (optional, for advanced URL extraction)

## 🚀 Installation

1. **Clone or download the project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys**:

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here  # Optional
FIRECRAWL_API_KEY=your-firecrawl-key-here  # Optional
```

## 💻 Usage

### Web UI (Recommended)

Launch the Gradio interface:

```bash
python main.py --mode ui
```

Access at: `http://localhost:7860`

For a public share link:
```bash
python main.py --mode ui --share
```

### CLI Mode

Process a file:
```bash
python main.py --mode cli \
  --input-type file \
  --input-data path/to/document.pdf \
  --num-questions 5 \
  --difficulty mixed
```

Process text:
```bash
python main.py --mode cli \
  --input-type text \
  --input-data "Your study material here..." \
  --num-questions 3
```

Process URL:
```bash
python main.py --mode cli \
  --input-type url \
  --input-data "https://example.com/article" \
  --num-questions 5
```

Web search:
```bash
python main.py --mode cli \
  --input-type search \
  --input-data "photosynthesis process" \
  --num-questions 5
```

## 📊 MLflow Tracking

View experiment tracking:

```bash
mlflow ui
```

Access at: `http://localhost:5000`

MLflow tracks:
- Processing time
- Summary length
- Number of key points
- Questions generated
- Success/failure status
- All generated artifacts

## 🎯 Use Cases

### For Students
- **Quick Review**: Upload lecture notes and get instant summaries
- **Self-Testing**: Generate practice quizzes from textbook chapters
- **Exam Prep**: Create custom quizzes at different difficulty levels
- **Research**: Search and summarize web content on topics

### For Teachers
- **Quiz Creation**: Auto-generate quiz questions from syllabus materials
- **Content Curation**: Extract key points from educational resources
- **Assignment Design**: Create varied difficulty assessments
- **Class Preparation**: Quick summaries of teaching materials

### For Self-Learners
- **Study Planning**: Break down complex topics into key points
- **Knowledge Testing**: Verify understanding with auto-generated quizzes
- **Content Aggregation**: Combine multiple sources via web search
- **Progress Tracking**: Use MLflow to track learning sessions

## 🔧 Configuration

### Adjust LLM Settings

Edit `config.py`:

```python
class Config:
    MODEL_NAME = "gpt-4-turbo-preview"  # Change model
    TEMPERATURE = 0.7                    # Adjust creativity
    CHUNK_SIZE = 1000                    # Document chunking
    MAX_SUMMARY_LENGTH = 500             # Summary word limit
    DEFAULT_NUM_QUESTIONS = 5            # Default quiz size
```

### Customize Quiz Generation

Modify difficulty levels and question types in `llm_chains.py`

## 📁 Project Structure

```
ai-study-assistant/
├── main.py                 # Entry point
├── ui.py                   # Gradio interface
├── agent.py                # LangGraph agent
├── config.py               # Configuration & state
├── document_processor.py   # Document handling
├── web_search.py          # Web search utilities
├── llm_chains.py          # LLM chains
├── mlflow_tracker.py      # MLflow integration
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🛠️ Extension Ideas

1. **Multi-User Study Groups**
   - Share quizzes between users
   - Collaborative study material curation
   - Leaderboards for quiz performance

2. **Advanced Quiz Types**
   - Fill-in-the-blank questions
   - Essay prompts with grading rubrics
   - Image-based questions
   - Code completion challenges

3. **Learning Analytics**
   - Track student progress over time
   - Identify weak areas
   - Personalized difficulty adjustment
   - Study time optimization

4. **Integration Options**
   - Google Classroom integration
   - Canvas LMS connector
   - Notion database sync
   - Discord/Slack bots

5. **Export Formats**
   - PDF quiz exports
   - Anki flashcard format
   - Kahoot quiz import
   - Google Forms generation

## 🐛 Troubleshooting

### Common Issues

**Import Errors**:
```bash
pip install --upgrade -r requirements.txt
```

**API Key Issues**:
- Verify `.env` file exists and contains valid keys
- Check key format (OpenAI: `sk-...`, Tavily: `tvly-...`)

**File Upload Errors**:
- Ensure supported file types (.pdf, .docx, .txt, .md)
- Check file is not corrupted
- Try reducing file size

**MLflow Connection Issues**:
```bash
# Reset MLflow
rm -rf mlruns/
```

## 📝 Example Workflow

1. **Upload Study Material**: Upload a PDF textbook chapter
2. **Review Summary**: Read the AI-generated summary
3. **Study Key Points**: Focus on extracted key concepts
4. **Take Quiz**: Test knowledge with generated questions
5. **Review Explanations**: Learn from detailed answer explanations
6. **Track Progress**: View metrics in MLflow UI

## 🤝 Contributing

Ideas for improvements:
- Better question quality validation
- Support for more document formats
- Multi-language support
- Voice input/output
- Mobile app version

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [OpenAI](https://openai.com/) - Language models
- [Gradio](https://gradio.app/) - UI framework
- [MLflow](https://mlflow.org/) - Experiment tracking
- [Tavily](https://tavily.com/) - Web search API

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review MLflow logs for detailed error info
3. Verify API keys and configuration

---

**Happy Studying! 🎓**