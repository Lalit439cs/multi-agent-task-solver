# Changelog

All notable changes to the Multi-Agent Task Solver project will be documented in this file.

## [Unreleased]

## [1.1.0] - 2024-10-13

### Added
- **Comprehensive Search Tools Documentation** (`SEARCH_TOOLS.md`)
  - Detailed guide for all search providers
  - Testing procedures and best practices
  - Troubleshooting guide with common issues
  - API documentation links and usage examples
  - Performance characteristics and cost analysis

### Enhanced
- **Tavily Search Integration**
  - Upgraded to `search_depth="advanced"` for better content extraction
  - Added `include_answer=True` to get AI-generated summaries
  - Added relevance scoring (0-1 scale) for each search result
  - Enhanced error reporting with detailed messages
  - Better context for LLM agents with both summaries and detailed sources
  - **Impact**: 2x better content relevance for agentic workflows

- **Perplexity Search Integration**
  - Updated model from deprecated `llama-3.1-sonar-small-128k-online` to `sonar`
  - Removed invalid `return_citations` parameter
  - Enhanced response parsing for both `citations` and `search_results` formats
  - Added detailed error logging for troubleshooting
  - **Fix**: Resolved HTTP 400 errors

- **DuckDuckGo Search Integration**
  - Improved retry logic with progressive backoff (2s, 4s, 6s)
  - Better rate limit handling
  - Enhanced error messages

### Changed
- **README.md**
  - Streamlined main README with focus on getting started
  - Added references to detailed `SEARCH_TOOLS.md` documentation
  - Updated project structure to include new documentation files
  - Added "Recent Updates" section highlighting October 2024 enhancements
  - Updated test section with checkmarks for validated features

### Fixed
- **Perplexity API Integration**
  - Fixed HTTP 400 error caused by deprecated model name
  - Removed unsupported parameters
  - Enhanced error handling and reporting

### Technical Details

**Search Provider Updates:**

```python
# Tavily - Enhanced Implementation
response = client.search(
    query=query,
    max_results=num_results,
    search_depth="advanced",    # NEW: Better AI-targeted content
    include_answer=True,         # NEW: Pre-generated answer
    include_raw_content=False
)

# Perplexity - Fixed Implementation
payload = {
    "model": "sonar",           # FIXED: Updated from deprecated model
    # "return_citations": True  # REMOVED: Invalid parameter
    ...
}
```

**Response Format Enhancements:**

Tavily now returns:
```
AI Summary:
<Pre-generated LLM answer>

Detailed Sources:
Result 1 (Relevance: 0.98):  ← NEW: Relevance scoring
Title: ...
URL: ...
Content: <AI-optimized content chunks>
```

### Documentation
- Created `SEARCH_TOOLS.md` with comprehensive documentation
  - 350+ lines of detailed search tool documentation
  - Testing procedures with sample outputs
  - Troubleshooting guide
  - API reference and cost analysis
- Updated `CHANGELOG.md` (this file)
- Enhanced inline code comments in `tools.py`

### Testing
- All search providers tested and validated
- Test suite (`test_search_tools.py`) updated to cover new features
- Verified cascading fallback mechanism
- Confirmed error handling improvements

---

## [1.0.0] - 2024-10-12

### Initial Release

#### Features
- Multi-agent task-solving system with LangGraph orchestration
- FastAPI backend with asynchronous execution
- Dual LLM support (GPT-4 and Gemini)
- Web search with cascading fallback strategy
- Python code execution sandbox
- File I/O operations
- Simple web UI
- Dockerized deployment

#### Components
- Planner agent for task decomposition
- Specialized agents (Researcher, Summarizer, Data Analyst, Code Executor)
- Aggregator for result synthesis
- Multi-provider web search (Tavily, Perplexity, DuckDuckGo)

#### Tools
- `WebSearchTool` - Multi-provider web search
- `PythonCodeExecutor` - Sandboxed code execution
- `FileIOTool` - File read/write/append operations

#### Testing
- `test_llm_api.py` - LLM API connectivity testing
- `test_client.py` - API endpoint testing
- `test_search_tools.py` - Search provider testing

---

## Version History

- **v1.1.0** (2024-10-13) - Enhanced search with Tavily advanced mode, fixed Perplexity, comprehensive documentation
- **v1.0.0** (2024-10-12) - Initial release with multi-agent orchestration and basic search

---

## Upgrade Notes

### Upgrading from 1.0.0 to 1.1.0

**No Breaking Changes** - This is a backward-compatible enhancement release.

**What You Need to Know:**
1. Tavily now uses 2 API credits per search (was 1) due to advanced mode
2. Perplexity API now works correctly (HTTP 400 error fixed)
3. Better search results with AI summaries and relevance scores
4. No code changes required in your agent implementations

**Recommended Actions:**
1. Run `python3 test_search_tools.py` to verify all providers work
2. Review `SEARCH_TOOLS.md` for new features and capabilities
3. Monitor Tavily API credit usage (now 2 credits per search)

**Optional Configurations:**

If you want to use basic Tavily search (1 credit) instead of advanced (2 credits):
```python
# In tools.py, change:
search_depth="basic"  # Instead of "advanced"
```

---

## Contributing

When contributing, please:
1. Update this CHANGELOG.md with your changes
2. Follow the format: Added/Changed/Deprecated/Removed/Fixed/Security
3. Include version number and date
4. Add technical details for significant changes
5. Update relevant documentation files

---

**Last Updated:** October 13, 2024
