# Quick Reference Guide

Quick reference for common tasks and configurations in the Multi-Agent Task Solver.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository_url>
cd multi-agent-task-solver

# 2. Create .env file (see below for template)
cp .env.example .env  # Edit with your API keys

# 3. Test APIs
python3 test_llm_api.py        # Test LLM connectivity
python3 test_search_tools.py   # Test search providers

# 4. Run application
docker build -t multi-agent-task-solver .
docker run -p 8000:8000 --env-file .env multi-agent-task-solver

# 5. Access UI
# Open: http://localhost:8000
```

## 🔑 Environment Variables Template

```bash
# LLM APIs (Required - at least one)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GEMINI_PROJECT_ID=your-project-id

# Search APIs (Optional but recommended)
TAVILY_API_KEY=tvly-...      # 1,000 free credits/month
PERPLEXITY_API_KEY=pplx-...  # Check pricing

# Model Configuration
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.5-pro

# Search Configuration
SEARCH_ENABLED=true
```

## 🔍 Search Providers - Quick Comparison

| Provider | Status | Cost | Speed | Quality | Use Case |
|----------|--------|------|-------|---------|----------|
| **Tavily** | ✅ Enhanced | 2 credits | Fast (2-4s) | ⭐⭐⭐⭐⭐ | Research, analysis |
| **Perplexity** | ✅ Fixed | Varies | Medium (2-5s) | ⭐⭐⭐⭐ | Conversational queries |
| **DuckDuckGo** | ✅ Reliable | Free | Fast (1-3s) | ⭐⭐⭐ | General search, fallback |

## 🛠️ Common Commands

### Testing
```bash
# Test all search providers
python3 test_search_tools.py

# Test specific LLM
python3 test_llm_api.py

# Test API endpoints (requires running server)
python3 test_client.py
```

### Docker
```bash
# Build image
docker build -t multi-agent-task-solver .

# Run container
docker run -p 8000:8000 --env-file .env -v $(pwd)/temp:/app/temp multi-agent-task-solver

# Stop container
docker ps  # Get container ID
docker stop <container_id>
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run without Docker
python3 main.py

# Check configuration
python3 check_auth.py
```

## 📊 API Endpoints

```
GET  /                    # Web UI
POST /api/task           # Submit new task
GET  /api/task/{task_id} # Get task status
```

### Example API Call

```bash
curl -X POST http://localhost:8000/api/task \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Latest AI developments in 2024",
    "use_gpt4": true,
    "use_gemini": false
  }'
```

## 🔧 Configuration Quick Fixes

### Issue: Perplexity HTTP 400
```bash
# ✅ Fixed in v1.1.0
# Update to latest code and retest
python3 test_search_tools.py
```

### Issue: Tavily Rate Limit
```python
# Option 1: Use basic search (1 credit instead of 2)
# In tools.py, line 90:
search_depth="basic"

# Option 2: Get more credits
# Visit: https://app.tavily.com/
```

### Issue: All Search Providers Failed
```bash
# 1. Check API keys
cat .env | grep API_KEY

# 2. Test individually
python3 test_search_tools.py

# 3. Check internet connectivity
ping google.com
```

## 📝 Search Tool Code Examples

### Basic Usage
```python
from tools import WebSearchTool

search = WebSearchTool()
results = search.run("your query", num_results=5)
print(results)
```

### What You Get Back

```
AI Summary:
<Pre-generated answer synthesizing all sources>

Detailed Sources:
Result 1 (Relevance: 0.98):
Title: Article Title
URL: https://source-url.com
Content: <AI-extracted relevant content>
```

### Test Individual Providers
```python
from tools import WebSearchTool

tool = WebSearchTool()

# Test Tavily
result = tool._search_with_tavily("AI trends 2024", 3)

# Test Perplexity
result = tool._search_with_perplexity("AI trends 2024", 3)

# Test DuckDuckGo
result = tool._search_with_duckduckgo("AI trends 2024", 3)
```

## 🎯 Agent Types

| Agent | Purpose | Tools Used |
|-------|---------|------------|
| **Researcher** | Web search & information gathering | `web_search_tool` |
| **Summarizer** | Condense and synthesize information | None (LLM only) |
| **Data Analyst** | Process data, create visualizations | `python_executor_tool` |
| **Code Executor** | Execute Python code | `python_executor_tool` |

## 💡 Best Practices

### Search Queries
```python
# ✅ Good
"latest advancements in quantum computing 2024"
"best practices for microservices architecture"
"current stock price NVDA and market trends"

# ❌ Avoid
"technology"  # Too generic
"news"        # Too broad
```

### Task Requests
```python
# ✅ Good - Specific and actionable
"Summarize the latest news on AI advancements and provide key statistics"
"Find NVIDIA's current stock price and explain recent trends"

# ❌ Avoid - Too vague
"Tell me about AI"
"What's happening in tech?"
```

## 📚 Documentation Quick Links

- **Main README**: [README.md](README.md) - Project overview
- **Search Guide**: [SEARCH_TOOLS.md](SEARCH_TOOLS.md) - Detailed search documentation
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history

## 🐛 Troubleshooting Quick Guide

| Error | Quick Fix |
|-------|-----------|
| HTTP 400 (Perplexity) | ✅ Fixed in v1.1.0 - Update code |
| Rate limit (Tavily) | Switch to `search_depth="basic"` or upgrade plan |
| Rate limit (DuckDuckGo) | ✅ Auto-retries - Just wait |
| All searches failed | Check API keys in `.env`, test with `test_search_tools.py` |
| LLM API errors | Verify keys with `test_llm_api.py` |

## 📞 Support

- **Detailed Docs**: See [SEARCH_TOOLS.md](SEARCH_TOOLS.md) for comprehensive guide
- **API Keys**: 
  - Tavily: https://app.tavily.com/
  - Perplexity: https://www.perplexity.ai/
  - OpenAI: https://platform.openai.com/
  - Google: https://makersuite.google.com/

## 🔄 Recent Updates (v1.1.0)

- ✅ Tavily: Advanced search with AI summaries & relevance scoring
- ✅ Perplexity: Fixed HTTP 400 error, updated model
- ✅ DuckDuckGo: Enhanced retry logic
- ✅ Documentation: Comprehensive search guide added

---

**Last Updated:** October 13, 2024  
**Version:** 1.1.0
