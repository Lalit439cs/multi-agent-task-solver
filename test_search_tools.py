#!/usr/bin/env python3
"""
Test script for web search tools.
Tests Tavily, Perplexity, and DuckDuckGo search independently.
"""

import sys
from datetime import datetime
from config import Config
from tools import WebSearchTool


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}\n")


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text):
    """Print info message."""
    print(f"→ {text}")


def print_result(result_text):
    """Print formatted search result."""
    print(f"{'-'*70}")
    print(result_text)
    print(f"{'-'*70}\n")


def test_tavily_search(query: str = "latest advancements in AI 2024"):
    """Test Tavily search independently."""
    print_header("Test 1: Tavily Search")
    
    if not Config.TAVILY_API_KEY:
        print_error("Tavily API key not found in .env file")
        print_info("Set TAVILY_API_KEY in your .env file to test Tavily")
        return False
    
    print_info(f"Testing Tavily search with query: '{query}'")
    print_info(f"API Key configured: {Config.TAVILY_API_KEY[:8]}...")
    
    try:
        tool = WebSearchTool()
        result = tool._search_with_tavily(query, num_results=3)
        
        if result:
            print_success("Tavily search successful!")
            print_result(result)
            return True
        else:
            print_error("Tavily search returned no results")
            return False
            
    except Exception as e:
        print_error(f"Tavily search failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_perplexity_search(query: str = "latest advancements in AI 2024"):
    """Test Perplexity search independently."""
    print_header("Test 2: Perplexity Search")
    
    if not Config.PERPLEXITY_API_KEY:
        print_error("Perplexity API key not found in .env file")
        print_info("Set PERPLEXITY_API_KEY in your .env file to test Perplexity")
        return False
    
    print_info(f"Testing Perplexity search with query: '{query}'")
    print_info(f"API Key configured: {Config.PERPLEXITY_API_KEY[:8]}...")
    
    try:
        tool = WebSearchTool()
        result = tool._search_with_perplexity(query, num_results=3)
        
        if result:
            print_success("Perplexity search successful!")
            print_result(result)
            return True
        else:
            print_error("Perplexity search returned no results")
            return False
            
    except Exception as e:
        print_error(f"Perplexity search failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_duckduckgo_search(query: str = "latest advancements in AI 2024"):
    """Test DuckDuckGo search independently."""
    print_header("Test 3: DuckDuckGo Search")
    
    print_info(f"Testing DuckDuckGo search with query: '{query}'")
    print_info("No API key required for DuckDuckGo")
    
    try:
        tool = WebSearchTool()
        result = tool._search_with_duckduckgo(query, num_results=3, max_retries=2)
        
        if result:
            print_success("DuckDuckGo search successful!")
            print_result(result)
            return True
        else:
            print_error("DuckDuckGo search returned no results")
            print_info("This may be due to rate limiting. Try again in a few minutes.")
            return False
            
    except Exception as e:
        print_error(f"DuckDuckGo search failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_cascading_search(query: str = "latest advancements in AI 2024"):
    """Test the full cascading search mechanism."""
    print_header("Test 4: Cascading Search (Full Integration)")
    
    print_info(f"Testing cascading search with query: '{query}'")
    print_info("This will try Tavily → Perplexity → DuckDuckGo")
    
    try:
        tool = WebSearchTool()
        result = tool.run(query, num_results=3)
        
        if result and "All search providers failed" not in result:
            print_success("Cascading search successful!")
            print_result(result)
            return True
        else:
            print_error("All search providers failed")
            return False
            
    except Exception as e:
        print_error(f"Cascading search failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_different_queries():
    """Test with different types of queries."""
    print_header("Test 5: Different Query Types")
    
    queries = [
        ("General knowledge", "What is quantum computing?"),
        ("Recent news", "latest developments in electric vehicles 2024"),
        ("Technical query", "how to implement REST API in Python"),
    ]
    
    tool = WebSearchTool()
    results = []
    
    for query_type, query in queries:
        print_info(f"Testing {query_type}: '{query}'")
        try:
            result = tool.run(query, num_results=2)
            if result and "All search providers failed" not in result:
                print_success(f"{query_type} search successful")
                results.append(True)
            else:
                print_error(f"{query_type} search failed")
                results.append(False)
        except Exception as e:
            print_error(f"{query_type} search exception: {str(e)}")
            results.append(False)
        print()
    
    success_rate = sum(results) / len(results) * 100
    print_info(f"Success rate: {success_rate:.0f}% ({sum(results)}/{len(results)} queries)")
    
    return all(results)


def print_configuration_summary():
    """Print a summary of the current configuration."""
    print_header("Configuration Summary")
    
    print("LLM Configuration:")
    print(f"  OpenAI API Key: {'✓ Configured' if Config.OPENAI_API_KEY else '✗ Not configured'}")
    print(f"  Google API Key: {'✓ Configured' if Config.GOOGLE_API_KEY else '✗ Not configured'}")
    
    print("\nSearch API Configuration:")
    print(f"  Tavily API Key: {'✓ Configured' if Config.TAVILY_API_KEY else '○ Not configured (optional)'}")
    print(f"  Perplexity API Key: {'✓ Configured' if Config.PERPLEXITY_API_KEY else '○ Not configured (optional)'}")
    print(f"  DuckDuckGo: ✓ Always available (no API key)")
    
    print("\nSearch Priority (Cascading Fallback):")
    priority = []
    if Config.TAVILY_API_KEY:
        priority.append("1. Tavily (Premium)")
    if Config.PERPLEXITY_API_KEY:
        priority.append(f"{len(priority) + 1}. Perplexity (AI-Powered)")
    priority.append(f"{len(priority) + 1}. DuckDuckGo (Free Fallback)")
    
    for item in priority:
        print(f"  {item}")


def main():
    """Main test runner."""
    print(f"\n{'='*70}")
    print(f"{'Web Search Tools Test Suite'.center(70)}")
    print(f"{'='*70}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Print configuration
    print_configuration_summary()
    
    # Test query
    test_query = "latest advancements in quantum computing 2024"
    
    # Run individual tests
    results = {
        "Tavily": test_tavily_search(test_query),
        "Perplexity": test_perplexity_search(test_query),
        "DuckDuckGo": test_duckduckgo_search(test_query),
        "Cascading": test_cascading_search(test_query),
    }
    
    # Run multi-query test
    # results["Multi-Query"] = test_with_different_queries()
    
    # Print summary
    print_header("Test Summary")
    
    print("Individual Test Results:")
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        elif passed is False:
            print_error(f"{test_name}: FAILED")
        else:
            print(f"→ {test_name}: SKIPPED (not configured)")
    
    total_tests = sum(1 for v in results.values() if v is not None)
    passed_tests = sum(1 for v in results.values() if v is True)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print_success("All tests passed!")
        return 0
    elif passed_tests > 0:
        print("⚠ Some tests failed. Check your API keys and network connection.")
        return 1
    else:
        print_error("All tests failed. Please check your configuration.")
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
