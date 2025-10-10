from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, Any, Optional
import os
from datetime import datetime

from orchestrator import MultiAgentOrchestrator

app = FastAPI(title="Multi-Agent Task Solver", version="1.0.0")

# Mount static files for the UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for task status (in production, use Redis or a database)
task_storage: Dict[str, Dict[str, Any]] = {}

class TaskRequest(BaseModel):
    request: str
    use_gpt4: Optional[bool] = True
    use_gemini: Optional[bool] = False

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main UI page."""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Multi-Agent Task Solver</h1><p>UI not found. Please ensure static/index.html exists.</p>")

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Create a new task and start processing it in the background."""
    task_id = str(uuid.uuid4())
    
    # Initialize task status
    task_storage[task_id] = {
        "status": "pending",
        "message": "Task created, starting processing...",
        "request": task_request.request,
        "created_at": datetime.now().isoformat(),
        "progress": [],
        "result": None,
        "error": None
    }
    
    # Start background processing
    background_tasks.add_task(process_task, task_id, task_request)
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Task created and processing started"
    )

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the current status of a task."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return JSONResponse(content=task_storage[task_id])

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    return JSONResponse(content={"tasks": list(task_storage.keys())})

async def process_task(task_id: str, task_request: TaskRequest):
    """Background task processing function."""
    print(f"\n{'='*60}", flush=True)
    print(f"STARTING TASK PROCESSING: {task_id}", flush=True)
    print(f"Request: {task_request.request}", flush=True)
    print(f"Use GPT-4: {task_request.use_gpt4}, Use Gemini: {task_request.use_gemini}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    try:
        # Update status to processing
        task_storage[task_id]["status"] = "processing"
        task_storage[task_id]["message"] = "Processing with multi-agent system..."
        
        print(f"Initializing orchestrator...", flush=True)
        # Initialize the orchestrator
        orchestrator = MultiAgentOrchestrator(
            use_gpt4=task_request.use_gpt4,
            use_gemini=task_request.use_gemini
        )
        print(f"Orchestrator initialized successfully", flush=True)
        
        print(f"Starting task execution...", flush=True)
        # Process the task
        result = await orchestrator.execute_task(
            task_request.request,
            progress_callback=lambda msg: update_task_progress(task_id, msg)
        )
        
        # Update with final result
        print(f"Task completed successfully!", flush=True)
        task_storage[task_id]["status"] = "completed"
        task_storage[task_id]["message"] = "Task completed successfully"
        task_storage[task_id]["result"] = result
        task_storage[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        # Update with error
        print(f"\n{'!'*60}", flush=True)
        print(f"ERROR in task {task_id}: {type(e).__name__}", flush=True)
        print(f"Error message: {str(e)}", flush=True)
        print(f"Error repr: {repr(e)}", flush=True)
        import traceback
        print(f"Full traceback:", flush=True)
        traceback.print_exc()
        print(f"{'!'*60}\n", flush=True)
        
        task_storage[task_id]["status"] = "error"
        task_storage[task_id]["message"] = f"Task failed: {str(e)}"
        task_storage[task_id]["error"] = str(e)
        task_storage[task_id]["completed_at"] = datetime.now().isoformat()

def update_task_progress(task_id: str, message: str):
    """Update task progress."""
    if task_id in task_storage:
        task_storage[task_id]["progress"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
