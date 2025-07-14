# 🧠 Reality Check Bot

**Validate emotionally charged topics with Reddit, web, and academic research**

## 🎯 Purpose

Help users understand whether a personal/political/problematic topic is commonly discussed, what solutions exist, and what perspectives are emerging by combining:

- Reddit community discussions
- Current web content
- Academic research papers
- AI-powered synthesis

## 🏗️ How It Works

**LangGraph Agent Flow:**

```
[Input Topic]
→ [Reddit Search via Tavily]
→ [Web Search via Tavily]
→ [Academic Search via Arxiv]
→ [LLM Synthesis via OpenAI]
→ [Structured Analysis Output]
```

LangSmith tracing is used for debugging and observability.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Tavily API key
- LangSmith API key (optional)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_key
# TAVILY_API_KEY=your_tavily_key
# LANGCHAIN_API_KEY=your_langsmith_key (optional)
```

### 3. Run the Application

**Option A: Web Interface (Recommended)**

```bash
python app.py
# Visit http://localhost:8000
```

**Option B: Command Line**

```bash
python main.py
```

## 🌐 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variables in Vercel dashboard
```

Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔧 API Endpoints

| Method | Endpoint    | Description                 |
| ------ | ----------- | --------------------------- |
| `GET`  | `/`         | Web interface               |
| `POST` | `/analyze`  | Analyze topic (JSON API)    |
| `GET`  | `/health`   | Health check                |
| `GET`  | `/test`     | Test endpoint for debugging |
| `GET`  | `/api/docs` | API documentation           |

### Example API Usage

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"topic": "impostor syndrome in software engineering"}'
```

## 📊 Output Format

The agent provides structured analysis in 4 sections:

- **🧠 What people are saying on Reddit**: Community discussions and personal experiences
- **🌐 Broader web context**: Current articles, discussions, and perspectives
- **📚 Academic research insights**: Peer-reviewed research and studies
- **🚀 Gaps or opportunities**: Unmet needs and potential solutions

## 🛠️ Project Structure

```
reality_check_agent/
├── app.py              # FastAPI web application
├── main.py             # Command-line interface
├── agent_graph.py      # LangGraph workflow definition
├── agent_state.py      # State management
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
├── vercel.json         # Vercel deployment config
├── static/
│   └── index.html      # Web frontend
└── tools/
    ├── reddit_search.py    # Reddit search via Tavily
    ├── tavily_search.py    # General web search
    ├── arxiv_search.py     # Academic paper search
    └── llm_reasoner.py     # OpenAI synthesis
```

## 🎯 Tech Stack

- **Backend**: FastAPI + LangGraph + LangChain
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **AI**: OpenAI GPT-4o
- **Search**: Tavily API (Reddit + Web)
- **Academic**: Arxiv API
- **Deployment**: Vercel
- **Observability**: LangSmith (optional)

## 🎨 Features

- **Professional UI**: Modern gradient design with real-time progress
- **Mobile-Friendly**: Responsive layout for all devices
- **Example Topics**: One-click topic suggestions
- **Error Handling**: Graceful failure handling
- **API & Web**: Both JSON API and web interface

## 🔍 Example Topics

- "impostor syndrome in software engineering"
- "remote work loneliness"
- "burnout in healthcare workers"
- "social media addiction"
- "climate change anxiety"

## 🧪 Testing

```bash
# Test all imports and environment
curl http://localhost:8000/test

# Check health status
curl http://localhost:8000/health

# Get API documentation
curl http://localhost:8000/api/docs
```

## 🎭 Perfect For

- **Product Validation**: Research market problems
- **Content Research**: Understand topic landscapes
- **Academic Research**: Find related studies
- **Market Analysis**: Identify gaps and opportunities
- **Personal Learning**: Explore complex topics thoroughly

---

**Need help?** Check out [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.
