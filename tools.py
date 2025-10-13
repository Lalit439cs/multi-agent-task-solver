import io
import sys
import json
import os
import time
import httpx
from typing import Optional, List, Dict
from duckduckgo_search import DDGS
from config import Config

# Optional imports for search providers
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Tavily not available. Install with: pip install tavily-python")

class Tool:
    def run(self, *args, **kwargs):
        raise NotImplementedError("Each tool must implement its own run method.")

class PythonCodeExecutor(Tool):
    def execute(self, code: str) -> str:
        # WARNING: This is a simplified and INSECURE Python code executor for demonstration purposes.
        # In a production environment, NEVER use exec() or eval() directly with untrusted input.
        # A secure sandbox (e.g., separate container, restricted environment) is CRITICAL.
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        try:
            # Define a dictionary to capture local variables after execution
            local_scope = {}
            exec(code, {}, local_scope)
            output = redirected_output.getvalue()
            # Attempt to return a 'result' variable if it was set by the executed code
            if 'result' in local_scope:
                return f"Output: {output.strip()}\nResult variable: {local_scope['result']}"
            return f"Output: {output.strip()}"
        except Exception as e:
            return f"Error during code execution: {e}"
        finally:
            sys.stdout = old_stdout # Restore original stdout

class WebSearchTool(Tool):
    """
    Web search tool with cascading fallback strategy:
    1. Tavily (premium search API)
    2. Perplexity (AI-powered search)
    3. DuckDuckGo (free fallback)
    """
    
    def run(self, query: str, num_results: int = 5) -> str:
        """Performs a web search with cascading fallback strategy."""
        print(f"\n{'='*60}", flush=True)
        print(f"WEB SEARCH REQUEST: {query}", flush=True)
        print(f"{'='*60}\n", flush=True)
        
        # Try Tavily first
        result = self._search_with_tavily(query, num_results)
        if result:
            return result
        
        # Try Perplexity second
        result = self._search_with_perplexity(query, num_results)
        if result:
            return result
        
        # Fall back to DuckDuckGo
        result = self._search_with_duckduckgo(query, num_results)
        if result:
            return result
        
        return "All search providers failed. Unable to retrieve web results."
    
    def _search_with_tavily(self, query: str, num_results: int) -> Optional[str]:
        """Search using Tavily API."""
        if not Config.TAVILY_API_KEY or not TAVILY_AVAILABLE:
            print("⊘ Tavily: Not configured or not available", flush=True)
            return None
        
        try:
            print("→ Trying Tavily...", flush=True)
            client = TavilyClient(api_key=Config.TAVILY_API_KEY)
            response = client.search(query=query, max_results=num_results)
            
            if response and 'results' in response:
                results = response['results']
                if results:
                    formatted_results = []
                    for i, res in enumerate(results):
                        formatted_results.append(
                            f"Result {i+1}:\n"
                            f"Title: {res.get('title', 'N/A')}\n"
                            f"URL: {res.get('url', 'N/A')}\n"
                            f"Snippet: {res.get('content', 'N/A')}\n"
                        )
                    print("✓ Tavily: Success", flush=True)
                    return "\n".join(formatted_results)
            
            print("⊘ Tavily: No results found", flush=True)
            return None
            
        except Exception as e:
            print(f"✗ Tavily failed: {str(e)}", flush=True)
            return None
    
    def _search_with_perplexity(self, query: str, num_results: int) -> Optional[str]:
        """Search using Perplexity API."""
        if not Config.PERPLEXITY_API_KEY:
            print("⊘ Perplexity: Not configured", flush=True)
            return None
        
        try:
            print("→ Trying Perplexity...", flush=True)
            
            headers = {
                "Authorization": f"Bearer {Config.PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful search assistant. Provide concise, factual information from web sources."
                    },
                    {
                        "role": "user",
                        "content": f"Search and provide information about: {query}"
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.2,
                "return_citations": True,
                "search_recency_filter": "month"
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    citations = data.get('citations', [])
                    
                    if content:
                        result = f"Search Results:\n{content}\n"
                        if citations:
                            result += "\n\nSources:\n"
                            for i, citation in enumerate(citations[:num_results], 1):
                                result += f"{i}. {citation}\n"
                        
                        print("✓ Perplexity: Success", flush=True)
                        return result
                else:
                    print(f"✗ Perplexity failed: HTTP {response.status_code}", flush=True)
            
            return None
            
        except Exception as e:
            print(f"✗ Perplexity failed: {str(e)}", flush=True)
            return None
    
    def _search_with_duckduckgo(self, query: str, num_results: int, max_retries: int = 3) -> Optional[str]:
        """Search using DuckDuckGo (free fallback)."""
        print("→ Trying DuckDuckGo (fallback)...", flush=True)
        
        for attempt in range(max_retries):
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=num_results))
                    if results:
                        formatted_results = []
                        for i, res in enumerate(results):
                            formatted_results.append(
                                f"Result {i+1}:\n"
                                f"Title: {res.get('title')}\n"
                                f"URL: {res.get('href')}\n"
                                f"Snippet: {res.get('body')}\n"
                            )
                        print("✓ DuckDuckGo: Success", flush=True)
                        return "\n".join(formatted_results)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"DuckDuckGo attempt {attempt + 1}/{max_retries} failed: {error_msg}", flush=True)
                
                # Check if it's a rate limit error
                if "Ratelimit" in error_msg or "429" in error_msg or "202" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Progressive backoff: 2s, 4s, 6s
                        print(f"Rate limited. Waiting {wait_time} seconds before retry...", flush=True)
                        time.sleep(wait_time)
                        continue
                
                if attempt == max_retries - 1:
                    print(f"✗ DuckDuckGo failed after {max_retries} attempts", flush=True)
                    return None
        
        return None

class FileIOTool(Tool):
    def read(self, path: str) -> str:
        """Reads content from a file."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found at {path}"
        except Exception as e:
            return f"Error reading file {path}: {e}"

    def write(self, path: str, content: str) -> str:
        """Writes content to a file, overwriting if it exists."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return f"Content successfully written to {path}"
        except Exception as e:
            return f"Error writing to file {path}: {e}"

    def append(self, path: str, content: str) -> str:
        """Appends content to a file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'a') as f:
                f.write(content)
            return f"Content successfully appended to {path}"
        except Exception as e:
            return f"Error appending to file {path}: {e}"
