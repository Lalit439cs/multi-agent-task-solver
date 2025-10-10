import io
import sys
import json
import os
import time
from duckduckgo_search import DDGS

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
    def run(self, query: str, num_results: int = 5, max_retries: int = 3) -> str:
        """Performs a web search using DuckDuckGo and returns the top results."""
        print(f"Performing web search for: {query}", flush=True)
        
        for attempt in range(max_retries):
            try:
                # Use DDGS with the updated API
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
                        return "\n".join(formatted_results)
                    return "No search results found."
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Web search attempt {attempt + 1}/{max_retries} failed: {error_msg}", flush=True)
                
                # Check if it's a rate limit error
                if "Ratelimit" in error_msg or "429" in error_msg or "202" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # Progressive backoff: 2s, 4s, 6s
                        print(f"Rate limited. Waiting {wait_time} seconds before retry...", flush=True)
                        time.sleep(wait_time)
                        continue
                    else:
                        return (
                            f"Web search failed due to rate limiting after {max_retries} attempts. "
                            f"Please try again later or use cached knowledge."
                        )
                else:
                    # For other errors, don't retry
                    print(f"Non-retryable error during web search: {e}", flush=True)
                    return f"Error during web search: {e}"
        
        return "Web search failed after all retry attempts."

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
