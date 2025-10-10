"""
Simple test script to verify OpenAI and Gemini API connectivity
"""
import os
from dotenv import load_dotenv

# Change the import to the specific Vertex AI library
from langchain_google_vertexai import ChatVertexAI
# from langchain_google_genai import ChatGoogleGenerativeAI


# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API connection"""
    print("\n" + "="*60)
    print("Testing OpenAI API")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # Initialize the model
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.7,
            openai_api_key=api_key
        )
        
        print(f"✓ Model initialized: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
        
        # Test with a simple prompt
        print("📤 Sending test message...")
        response = llm.invoke("Say 'Hello! OpenAI is working!' in a friendly way.")
        
        print(f"✅ OpenAI API is working!")
        print(f"📥 Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed!")
        print(f"Error: {str(e)}")
        return False

def test_gemini():
    """Test Google Gemini API connection"""
    print("\n" + "="*60)
    print("Testing Google Gemini API")
    print("="*60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        
        # Initialize the model
        # llm = ChatGoogleGenerativeAI(
        llm = ChatVertexAI(
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            temperature=0.7,
            # google_api_key=api_key
            project_id=os.getenv("GEMINI_PROJECT_ID")
        )
        
        print(f"✓ Model initialized: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
        
        # Test with a simple prompt
        print("📤 Sending test message...")
        response = llm.invoke("Say 'Hello! Gemini is working!' in a friendly way.")
        
        print(f"✅ Gemini API is working!")
        print(f"📥 Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed!")
        print(f"Error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "🔧 LLM API Connectivity Test" + "\n")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found!")
        print("Please create a .env file with your API keys.")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-...")
        print("GOOGLE_API_KEY=AIza...")
        print("OPENAI_MODEL=gpt-4")
        print("GEMINI_MODEL=gemini-1.5-flash")
        return
    
    print("✓ .env file found\n")
    
    # Test APIs
    openai_works = test_openai()
    # openai_works = True
    gemini_works = test_gemini()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"OpenAI API: {'✅ Working' if openai_works else '❌ Failed'}")
    print(f"Gemini API: {'✅ Working' if gemini_works else '❌ Failed'}")
    
    if openai_works or gemini_works:
        print("\n✅ At least one API is working! You can proceed.")
    else:
        print("\n❌ No APIs are working. Please check your API keys in .env file.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
