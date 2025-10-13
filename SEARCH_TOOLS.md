# Web Search Tools Guide

This document provides detailed information about the web search capabilities in the Multi-Agent Task Solver, including the enhanced search implementations, testing procedures, and best practices.

## Table of Contents

- [Overview](#overview)
- [Search Providers](#search-providers)
- [Recent Enhancements](#recent-enhancements)
- [Configuration](#configuration)
- [Testing](#testing)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Overview

The Multi-Agent Task Solver implements an intelligent **cascading search strategy** with three providers:
1. **Tavily** (Premium, primary)
2. **Perplexity** (AI-powered, secondary)
3. **DuckDuckGo** (Free, final fallback)

When a search is requested, the system automatically tries each provider in order until it gets successful results, ensuring maximum reliability and uptime.

## Search Providers

### 1. Tavily Search (Primary - Recommended)

**Status:** ✅ Enhanced with Advanced Search Depth

**Features:**
- Advanced AI-powered content extraction
- Pre-generated LLM answers
- Relevance scoring for each result
- Query-optimized content chunks
- High-quality, curated results

**API Details:**
- **Website:** https://tavily.com/
- **Free Tier:** 1,000 credits/month (500 advanced searches)
- **Cost per Search:** 
  - Basic: 1 credit
  - Advanced: 2 credits (current implementation)

**What Tavily Returns to Your LLM:**

```
AI Summary:
<Pre-generated answer synthesizing all sources>

Detailed Sources:
Result 1 (Relevance: 0.98):
Title: Article Title
URL: https://source-url.com
Content: <Highly relevant, AI-extracted content chunks>

Result 2 (Relevance: 0.92):
...
```

**Recent Enhancements (2024):**
- ✅ `search_depth="advanced"` - Better targeted content extraction
- ✅ `include_answer=True` - AI-generated summary included
- ✅ Relevance scores for quality filtering
- ✅ Enhanced error reporting with detailed messages

### 2. Perplexity AI (Secondary)

**Status:** ✅ Fixed - Model Updated to Current Version

**Features:**
- Conversational AI-powered search
- Natural language responses
- Source citations
- Real-time web access

**API Details:**
- **Website:** https://www.perplexity.ai/
- **Model:** `sonar` (updated from deprecated model)
- **Context:** Supports up to 128k tokens

**Recent Fixes (October 2024):**
- ✅ Updated from deprecated `llama-3.1-sonar-small-128k-online` to `sonar`
- ✅ Removed invalid `return_citations` parameter
- ✅ Enhanced response parsing for both `citations` and `search_results`
- ✅ Added detailed error logging

**What Perplexity Returns:**

```
Search Results:
<AI-generated response with factual information>

Sources:
1. https://source1.com
2. https://source2.com
```

### 3. DuckDuckGo (Final Fallback)

**Status:** ✅ Always Available

**Features:**
- No API key required
- Privacy-focused search
- Rate-limiting with retry logic
- Free unlimited searches

**Implementation Details:**
- Automatic retries: 3 attempts
- Progressive backoff: 2s, 4s, 6s
- Handles rate limits gracefully

## Recent Enhancements

### October 2024 Updates

#### 1. Perplexity API Fix
**Issue:** HTTP 400 errors due to deprecated model
**Solution:** 
- Updated model name to `sonar`
- Removed invalid parameters
- Enhanced error handling

#### 2. Tavily Advanced Search
**Enhancement:** Upgraded from basic to advanced search
**Benefits:**
- 2x better content relevance
- AI-generated summaries included
- Relevance scores for filtering
- Query-optimized content chunks

**Code Changes:**
```python
# Before (Basic)
response = client.search(query=query, max_results=num_results)

# After (Advanced)
response = client.search(
    query=query,
    max_results=num_results,
    search_depth="advanced",  # Better AI-targeted content
    include_answer=True,      # Pre-generated answer
    include_raw_content=False # Can enable for full content
)
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Search API Keys (Optional - for enhanced web search)
TAVILY_API_KEY=your_tavily_api_key_here      # Premium search (recommended)
PERPLEXITY_API_KEY=your_perplexity_api_key   # AI-powered search (fallback)
# Note: DuckDuckGo requires no API key

# Search Configuration
SEARCH_ENABLED=true
```

### Getting API Keys

#### Tavily
1. Visit: https://tavily.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier: 1,000 credits/month

#### Perplexity
1. Visit: https://www.perplexity.ai/
2. Sign up and access the API section
3. Generate your API key
4. Check pricing at: https://docs.perplexity.ai/

## Testing

### Running the Test Suite

The project includes a comprehensive test suite for all search providers:

```bash
python3 test_search_tools.py
```

### What the Test Suite Does

The test script (`test_search_tools.py`) performs the following tests:

1. **Individual Provider Tests**
   - Test Tavily search (if API key configured)
   - Test Perplexity search (if API key configured)
   - Test DuckDuckGo search (always runs)

2. **Integration Tests**
   - Test cascading fallback mechanism
   - Test with different query types
   - Verify error handling

3. **Configuration Summary**
   - Show which APIs are configured
   - Display search priority order
   - Report test success rates

### Sample Test Output

```
======================================================================
                    Web Search Tools Test Suite                      
======================================================================
Started at: 2024-10-13 14:30:00

======================================================================
                      Configuration Summary                          
======================================================================

LLM Configuration:
  OpenAI API Key: ✓ Configured
  Google API Key: ✓ Configured

Search API Configuration:
  Tavily API Key: ✓ Configured
  Perplexity API Key: ✓ Configured
  DuckDuckGo: ✓ Always available (no API key)

Search Priority (Cascading Fallback):
  1. Tavily (Premium)
  2. Perplexity (AI-Powered)
  3. DuckDuckGo (Free Fallback)

======================================================================
                    Test 1: Tavily Search                           
======================================================================

→ Testing Tavily search with query: 'latest advancements in quantum computing 2024'
→ API Key configured: tvly-abc...
→ Trying Tavily...
✓ Tavily: Success
✓ Tavily search successful!
----------------------------------------------------------------------
AI Summary:
Recent advancements in quantum computing include...

Detailed Sources:
Result 1 (Relevance: 0.98):
Title: Quantum Computing Breakthroughs 2024
URL: https://example.com/quantum-2024
Content: Major developments in quantum computing...
----------------------------------------------------------------------

======================================================================
                    Test 2: Perplexity Search                       
======================================================================

→ Testing Perplexity search with query: 'latest advancements in quantum computing 2024'
→ API Key configured: pplx-xyz...
→ Trying Perplexity...
✓ Perplexity: Success
✓ Perplexity search successful!
----------------------------------------------------------------------
Search Results:
Quantum computing has seen significant progress in 2024...

Sources:
1. https://source1.com
2. https://source2.com
----------------------------------------------------------------------

======================================================================
                       Test Summary                                  
======================================================================

Individual Test Results:
✓ Tavily: PASSED
✓ Perplexity: PASSED
✓ DuckDuckGo: PASSED
✓ Cascading: PASSED

Overall: 4/4 tests passed
✓ All tests passed!
```

### Testing Individual Providers

You can test each provider independently in the code:

```python
from tools import WebSearchTool

tool = WebSearchTool()

# Test Tavily
result = tool._search_with_tavily("your query", num_results=3)
print(result)

# Test Perplexity
result = tool._search_with_perplexity("your query", num_results=3)
print(result)

# Test DuckDuckGo
result = tool._search_with_duckduckgo("your query", num_results=3)
print(result)

# Test cascading (automatic fallback)
result = tool.run("your query", num_results=5)
print(result)
```

## Usage Examples

### In Agent Workflows

The search tool is automatically available to agents in the orchestrator:

```python
# Agent using web search
agent_response = """
{
    "tool": "web_search_tool",
    "input": {
        "query": "latest AI developments 2024"
    }
}
"""
```

The agent receives formatted results:

```
AI Summary:
Major AI developments in 2024 include advances in large language models...

Detailed Sources:
Result 1 (Relevance: 0.98):
Title: AI Trends 2024
URL: https://ai-news.com/trends-2024
Content: The year 2024 has witnessed breakthrough developments...
```

### Direct Python Usage

```python
from tools import WebSearchTool

# Initialize the search tool
search_tool = WebSearchTool()

# Perform a search (automatic cascading)
results = search_tool.run(
    query="climate change solutions",
    num_results=5
)

print(results)
```

### Query Best Practices

**Good Queries:**
- ✅ "latest advancements in quantum computing 2024"
- ✅ "best practices for microservices architecture"
- ✅ "current stock price NVDA and market trends"

**Avoid:**
- ❌ Very generic terms: "technology", "news"
- ❌ Overly complex multi-part questions
- ❌ Questions requiring real-time data older than recent searches

## Troubleshooting

### Common Issues

#### 1. Perplexity HTTP 400 Error

**Problem:** Getting HTTP 400 errors from Perplexity

**Cause:** Using deprecated model names or invalid parameters

**Solution:** ✅ Already fixed in latest version
- Model updated to `sonar`
- Invalid parameters removed
- Run `test_search_tools.py` to verify

#### 2. Tavily Rate Limits

**Problem:** "Rate limit exceeded" error

**Cause:** Exceeded monthly credit limit (1,000 credits for free tier)

**Solutions:**
- Monitor usage at: https://app.tavily.com/
- Switch to `search_depth="basic"` to use fewer credits (1 vs 2)
- Upgrade to paid tier for more credits

#### 3. DuckDuckGo Rate Limiting

**Problem:** "Ratelimit" errors from DuckDuckGo

**Cause:** Too many requests in short time period

**Solutions:**
- ✅ Already handled with retry logic (automatic)
- The tool waits and retries (2s, 4s, 6s intervals)
- Consider setting up Tavily or Perplexity to avoid hitting DuckDuckGo

#### 4. All Providers Failing

**Problem:** Getting "All search providers failed" message

**Diagnosis:**
1. Check API keys in `.env` file
2. Run `python3 test_search_tools.py` to identify the issue
3. Check internet connectivity
4. Verify API key validity on provider dashboards

**Solutions:**
- Ensure at least one API key is configured
- Check for API service outages
- Review API key permissions and billing status

### Debug Mode

Enable detailed logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your search
search_tool = WebSearchTool()
result = search_tool.run("your query")
```

### Error Messages Reference

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "⊘ Tavily: Not configured" | API key missing | Add `TAVILY_API_KEY` to `.env` |
| "✗ Tavily failed: HTTP 401" | Invalid API key | Check API key in Tavily dashboard |
| "✗ Perplexity failed: HTTP 400" | ✅ Fixed | Update to latest code version |
| "DuckDuckGo attempt 1/3 failed: Ratelimit" | Rate limited | ✅ Automatic retry in progress |
| "All search providers failed" | All APIs unavailable | Check connectivity and API keys |

## Performance Characteristics

### Response Times (Approximate)

| Provider | Typical Response Time | Notes |
|----------|----------------------|-------|
| Tavily Advanced | 2-4 seconds | Higher quality results |
| Tavily Basic | 1-2 seconds | Faster but less targeted |
| Perplexity | 2-5 seconds | AI processing time |
| DuckDuckGo | 1-3 seconds | May vary with rate limits |

### Cost Analysis

**Free Tier Monthly Limits:**

| Provider | Free Tier | Cost per Search | Monthly Free Searches |
|----------|-----------|-----------------|----------------------|
| Tavily | 1,000 credits | 2 credits (advanced) | 500 advanced searches |
| Perplexity | Varies | Varies | Check pricing page |
| DuckDuckGo | Unlimited | Free | Unlimited (rate-limited) |

**Recommendation:**
- For development/testing: Use Tavily free tier + DuckDuckGo fallback
- For production: Consider Tavily paid tier for consistent performance

## API Documentation Links

- **Tavily:** https://docs.tavily.com/
- **Perplexity:** https://docs.perplexity.ai/
- **DuckDuckGo:** https://github.com/deedy5/duckduckgo_search

## Contributing

When enhancing search functionality:

1. Test changes with `test_search_tools.py`
2. Update this documentation
3. Ensure backward compatibility
4. Follow the cascading fallback pattern
5. Add appropriate error handling

## Changelog

### October 2024
- ✅ Fixed Perplexity API (model update)
- ✅ Enhanced Tavily with advanced search depth
- ✅ Added AI-generated summaries
- ✅ Added relevance scoring
- ✅ Improved error handling and logging
- ✅ Created comprehensive test suite

### Earlier
- Initial implementation with three-tier cascading search
- Basic Tavily, Perplexity, and DuckDuckGo integration

---

**Last Updated:** October 13, 2024
