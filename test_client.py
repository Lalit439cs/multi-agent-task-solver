import httpx
import asyncio
import json

async def test_task_creation_and_status( ):
    base_url = "http://localhost:8000"
    
    # Test 1: Create a task with GPT-4
    print("\n--- Test 1: Creating a task with GPT-4 ---" )
    task_request_gpt4 = {
        "request": "Summarize the latest advancements in quantum computing and provide key challenges.",
        "use_gpt4": True,
        "use_gemini": False
    }
    try:
        response = httpx.post(f"{base_url}/api/tasks", json=task_request_gpt4, timeout=60 )
        response.raise_for_status()
        task_response_gpt4 = response.json()
        task_id_gpt4 = task_response_gpt4["task_id"]
        print(f"Task created with GPT-4. Task ID: {task_id_gpt4}")
        await poll_task_status(base_url, task_id_gpt4)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error creating task with GPT-4: {e.response.status_code} - {e.response.text}" )
    except httpx.RequestError as e:
        print(f"Request error creating task with GPT-4: {e}" )

    # break
    return
    # Test 2: Create a task with Gemini
    print("\n--- Test 2: Creating a task with Gemini ---")
    task_request_gemini = {
        "request": "Explain the concept of blockchain technology and its potential applications in supply chain management.",
        "use_gpt4": False,
        "use_gemini": True
    }
    try:
        response = httpx.post(f"{base_url}/api/tasks", json=task_request_gemini, timeout=60 )
        response.raise_for_status()
        task_response_gemini = response.json()
        task_id_gemini = task_response_gemini["task_id"]
        print(f"Task created with Gemini. Task ID: {task_id_gemini}")
        await poll_task_status(base_url, task_id_gemini)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error creating task with Gemini: {e.response.status_code} - {e.response.text}" )
    except httpx.RequestError as e:
        print(f"Request error creating task with Gemini: {e}" )

    # Test 3: Create a task requiring web search and code execution
    print("\n--- Test 3: Creating a task with Web Search and Code Execution ---")
    task_request_complex = {
        "request": "Find the current stock price of Google (GOOGL) and calculate its 5-day moving average. Use web search for the stock price and Python for calculation.",
        "use_gpt4": True,
        "use_gemini": False
    }
    try:
        response = httpx.post(f"{base_url}/api/tasks", json=task_request_complex, timeout=60 )
        response.raise_for_status()
        task_response_complex = response.json()
        task_id_complex = task_response_complex["task_id"]
        print(f"Complex task created. Task ID: {task_id_complex}")
        await poll_task_status(base_url, task_id_complex)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error creating complex task: {e.response.status_code} - {e.response.text}" )
    except httpx.RequestError as e:
        print(f"Request error creating complex task: {e}" )

async def poll_task_status(base_url: str, task_id: str):
    status_url = f"{base_url}/api/tasks/{task_id}"
    while True:
        try:
            response = httpx.get(status_url, timeout=60 )
            response.raise_for_status()
            task_status = response.json()
            
            status = task_status["status"]
            message = task_status["message"]
            progress = task_status["progress"]
            result = task_status["result"]

            print(f"Task {task_id} Status: {status} - {message}")
            if progress:
                for log in progress:
                    print(f"  Progress: [{log['timestamp']}] {log['message']}")

            if status == "completed":
                print(f"Task {task_id} COMPLETED. Final Result:\n{result}")
                break
            elif status == "error":
                print(f"Task {task_id} FAILED. Error: {task_status.get('error', 'Unknown error')}")
                break
            
            await asyncio.sleep(5) # Poll every 5 seconds
        except httpx.HTTPStatusError as e:
            print(f"HTTP error polling task {task_id}: {e.response.status_code} - {e.response.text}" )
            break
        except httpx.RequestError as e:
            print(f"Request error polling task {task_id}: {e}" )
            break

if __name__ == "__main__":
    asyncio.run(test_task_creation_and_status())
