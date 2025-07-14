# 🚀 Reality Check Bot - Deployment Guide

## 🌐 Web App Structure

```
reality_check_agent/
├── app.py              # FastAPI web application
├── static/
│   └── index.html      # Frontend interface
├── vercel.json         # Vercel deployment config
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
└── agent/tool files... # LangGraph implementation
```

## 🔧 Quick Start (Local)

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set up environment:**

```bash
cp env.example .env
# Edit .env with your API keys
```

3. **Run locally:**

```bash
python app.py
```

Visit: `http://localhost:8000`

## ☁️ Deploy to Vercel (Recommended)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy

```bash
vercel --prod
```

### Step 3: Set Environment Variables

In Vercel dashboard, go to your project settings and add:

- `OPENAI_API_KEY` = your OpenAI API key
- `TAVILY_API_KEY` = your Tavily API key
- `LANGCHAIN_API_KEY` = your LangSmith key (optional)

### Step 4: Test Your Deployment

Your app will be live at: `https://your-project-name.vercel.app`

## 🎯 Features

- **Professional UI:** Clean, responsive design
- **Real-time Progress:** Shows search steps as they execute
- **Example Topics:** One-click topic suggestions
- **Error Handling:** Graceful failure handling
- **Mobile-Friendly:** Works on all devices

## 📊 API Endpoints

- `GET /` - Web interface
- `POST /analyze` - Analyze topic (JSON API)
- `GET /health` - Health check
- `GET /api/docs` - API documentation

## 🔍 Example Usage

**Via Web Interface:**

1. Enter topic: "impostor syndrome in software engineering"
2. Click "Analyze Topic"
3. Watch real-time progress
4. Get structured analysis

**Via API:**

```bash
curl -X POST "https://your-app.vercel.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{"topic": "impostor syndrome in software engineering"}'
```

## 🛠️ Tech Stack

- **Backend:** FastAPI + LangGraph + LangChain
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **AI:** OpenAI GPT-4o
- **Search:** Tavily API
- **Academic:** Arxiv API
- **Deployment:** Vercel
- **Observability:** LangSmith (optional)

## 🎨 UI Preview

- Modern gradient design
- Interactive loading states
- Structured analysis output
- Example topic suggestions
- Mobile-responsive layout

**Perfect for:**

- Product validation
- Research assistance
- Topic exploration
- Academic research
- Market analysis
