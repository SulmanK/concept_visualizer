# Backend Scaling Strategy for Concept Visualizer on Vercel

## Current Status
- FastAPI backend using a single worker
- Sequential request processing (no parallelism)
- Limited ability to handle concurrent users
- Targeted for Vercel deployment

## Requirements
- Deploy on Vercel's free tier
- Support up to 20 concurrent users (5 minimum)
- Optimize for cost efficiency (free tier usage)
- Maintain responsiveness under concurrent load

## Technical Constraints
- Vercel Serverless Functions have cold starts
- Free tier has limited execution time (10-60 seconds)
- Memory limits of 1024MB per function
- Concurrent execution limits on free tier

## Design Decisions

### 1. Serverless Deployment Architecture

Vercel's serverless architecture automatically provisions instances based on traffic, which helps with handling multiple users. However, we need to adapt our FastAPI application to work optimally in this environment:

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│  User Request  │────▶│  Vercel Edge   │────▶│  FastAPI       │
│                │     │  Network       │     │  Function      │
│                │     │                │     │                │
└────────────────┘     └────────────────┘     └────────────────┘
                                                      │
                                                      ▼
                             ┌──────────────────────────────────────┐
                             │                                      │
                             │  External Services (JigsawStack)     │
                             │                                      │
                             └──────────────────────────────────────┘
```

#### Implementation Plan:
1. Create a `vercel.json` configuration:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/app/main.py"
    }
  ]
}
```

2. Create an entry point specifically for Vercel:
```python
# backend/vercel_app.py
from app.main import app

# This exports the FastAPI app for Vercel serverless functions
```

### 2. Asynchronous Request Handling

FastAPI already supports async/await, but we need to ensure all endpoints use it effectively:

```python
@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(request: PromptRequest, service: ConceptService = Depends()):
    """
    Generate a concept based on logo and theme description.
    This is an async endpoint that doesn't block the worker.
    """
    return await service.generate_concept(request.logo_description, request.theme_description)
```

#### Benefits:
- Allows handling multiple requests concurrently within the same function instance
- Prevents blocking during I/O operations (like JigsawStack API calls)
- Makes efficient use of the limited resources on Vercel

### 3. Background Tasks for Long-Running Operations

For operations that take longer than a few seconds (like image generation), we'll use FastAPI's BackgroundTasks:

```python
@router.post("/generate-with-background", response_model=TaskResponse)
async def generate_with_background(
    request: PromptRequest, 
    background_tasks: BackgroundTasks,
    service: ConceptService = Depends()
):
    """
    Start a concept generation task in the background and return immediately.
    The client can poll for results.
    """
    task_id = str(uuid.uuid4())
    
    # Schedule the generation in the background
    background_tasks.add_task(
        service.generate_concept_and_store,
        task_id,
        request.logo_description, 
        request.theme_description
    )
    
    return {"task_id": task_id, "status": "processing"}
```

#### Why This Rather Than Celery/Redis:
- Simpler implementation that works within Vercel's serverless model
- No need for additional infrastructure (Redis server, worker processes)
- Suitable for our modest requirements (<20 concurrent users)
- Free tier compatible (no additional services to pay for)

### 4. Stateless Design with Supabase

To handle state across function invocations:

```python
@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: Database = Depends(get_db)):
    """
    Check the status of a background task.
    """
    result = await db.fetch_one(
        "SELECT status, result FROM tasks WHERE id = :task_id",
        {"task_id": task_id}
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {
        "task_id": task_id,
        "status": result["status"],
        "result": json.loads(result["result"]) if result["result"] else None
    }
```

### 5. Optimizing Response Times

To keep the application responsive:

1. **Timeout Management**:
```python
@router.post("/generate-optimized")
async def generate_optimized(request: PromptRequest):
    try:
        # Set a reasonable timeout for the operation
        result = await asyncio.wait_for(
            service.generate_concept(request.logo_description, request.theme_description),
            timeout=20.0  # 20 second timeout
        )
        return result
    except asyncio.TimeoutError:
        # Convert to background task if it's taking too long
        background_tasks.add_task(...)  # Schedule as background task
        return {"status": "processing", "message": "Task moved to background"}
```

2. **Response Streaming** (for progress updates):
```python
@router.get("/stream-progress/{task_id}")
async def stream_progress(task_id: str, request: Request):
    async def event_generator():
        while True:
            # Check progress in database
            progress = await db.fetch_one(
                "SELECT progress FROM tasks WHERE id = :task_id",
                {"task_id": task_id}
            )
            
            if not progress:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break
                
            yield f"data: {json.dumps({'progress': progress['progress']})}\n\n"
            
            if progress['progress'] == 100:
                break
                
            await asyncio.sleep(1)
    
    return EventSourceResponse(event_generator())
```

## Implementation Phases

### Phase 1: Vercel Configuration
- Create vercel.json
- Create Vercel entry point
- Test basic deployment

### Phase 2: Async Optimization
- Review and convert all endpoints to async
- Implement proper error handling for async operations
- Test with simulated concurrent requests

### Phase 3: Background Task Implementation
- Add BackgroundTasks support
- Create task status tracking in Supabase
- Add endpoints for checking task status

### Phase 4: Response Optimization
- Implement timeouts
- Add streaming progress updates
- Optimize JigsawStack API calls

### Phase 5: Testing & Monitoring
- Test with simulated concurrent users
- Implement basic monitoring
- Set up alerts for failures

## Implementation Plan: BackgroundTasks with Task Status Tracking

Given our image generation process takes around 60 seconds (which is at the limit of Vercel's serverless function timeout), we'll implement a pattern using FastAPI's BackgroundTasks combined with task status storage in Supabase.

### 1. Task Status Storage Schema

First, we need to create a table in Supabase to track task status:

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  session_id TEXT NOT NULL,
  status TEXT NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  request JSONB, -- Store the original request parameters
  result JSONB, -- Store the result when completed
  error TEXT -- Store error message if failed
);

-- Create an index for faster lookups by session
CREATE INDEX idx_tasks_session_id ON tasks(session_id);

-- Create an index for status to quickly find pending tasks
CREATE INDEX idx_tasks_status ON tasks(status);
```

### 2. Task Submission API

Create an endpoint that immediately returns a task ID and starts processing in the background:

```python
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
import uuid
import json
from datetime import datetime
from app.services.concept_service import ConceptService
from app.db.database import get_db

class PromptRequest(BaseModel):
    logo_description: str
    theme_description: str

@app.post("/api/concept/generate", response_model=TaskResponse)
async def generate_concept(
    request: PromptRequest, 
    background_tasks: BackgroundTasks,
    db = Depends(get_db),
    service: ConceptService = Depends()
):
    """
    Start a concept generation task and return immediately with a task ID.
    The actual processing happens in the background.
    """
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Get session ID from request cookies or create a new one
    session_id = request.cookies.get("concept_session")
    if not session_id:
        session_id = str(uuid.uuid4())
        # Will need to set this cookie in the response
    
    # Store task in database as 'pending'
    await db.execute(
        """
        INSERT INTO tasks (id, session_id, status, request, created_at, updated_at)
        VALUES (:id, :session_id, :status, :request, :created_at, :updated_at)
        """,
        {
            "id": task_id,
            "session_id": session_id,
            "status": "pending",
            "request": json.dumps(request.dict()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )
    
    # Add the task to background tasks
    background_tasks.add_task(
        process_generation_task,
        task_id,
        session_id,
        request.logo_description,
        request.theme_description,
        service,
        db
    )
    
    # Create response with a cookie for session tracking
    response = TaskResponse(task_id=task_id, status="pending")
    
    # If new session, set the cookie
    if not request.cookies.get("concept_session"):
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=True,
            max_age=60*60*24*30,  # 30 days
            samesite="lax"
        )
    
    return response
```

### 3. Background Task Processing Function

Implement the actual processing function that runs in the background:

```python
async def process_generation_task(
    task_id: str,
    session_id: str,
    logo_description: str,
    theme_description: str,
    service: ConceptService,
    db
):
    """Process the generation task in the background."""
    try:
        # Update status to processing
        await db.execute(
            "UPDATE tasks SET status = :status, updated_at = :updated_at WHERE id = :id",
            {"id": task_id, "status": "processing", "updated_at": datetime.utcnow()}
        )
        
        # Generate the concept - this is the long-running operation
        result = await service.generate_concept(logo_description, theme_description)
        
        # Update database with successful result
        await db.execute(
            """
            UPDATE tasks 
            SET status = :status, 
                result = :result, 
                updated_at = :updated_at 
            WHERE id = :id
            """,
            {
                "id": task_id, 
                "status": "completed", 
                "result": json.dumps(result), 
                "updated_at": datetime.utcnow()
            }
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error processing task {task_id}: {str(e)}")
        
        # Update database with error
        await db.execute(
            """
            UPDATE tasks 
            SET status = :status, 
                error = :error, 
                updated_at = :updated_at 
            WHERE id = :id
            """,
            {
                "id": task_id, 
                "status": "failed", 
                "error": str(e), 
                "updated_at": datetime.utcnow()
            }
        )
```

### 4. Task Status Checking API

Create an endpoint for the client to poll for task status:

```python
@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db = Depends(get_db)):
    """
    Get the status of a task by its ID.
    """
    task = await db.fetch_one(
        """
        SELECT id, status, result, error, created_at, updated_at
        FROM tasks 
        WHERE id = :id
        """,
        {"id": task_id}
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "task_id": task["id"],
        "status": task["status"],
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }
    
    # Include result if task is completed
    if task["status"] == "completed" and task["result"]:
        response["result"] = json.loads(task["result"])
    
    # Include error if task failed
    if task["status"] == "failed" and task["error"]:
        response["error"] = task["error"]
    
    return response
```

### 5. Frontend Integration

On the frontend, we'll need to implement a polling mechanism:

```typescript
// React hook for polling task status
function useTaskStatus(taskId: string | null) {
  const [status, setStatus] = useState<'pending' | 'processing' | 'completed' | 'failed' | null>(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    
    let intervalId: number;
    let isMounted = true;
    
    const checkStatus = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/tasks/${taskId}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch task status');
        }
        
        const data = await response.json();
        
        if (isMounted) {
          setStatus(data.status);
          
          if (data.result) {
            setResult(data.result);
          }
          
          if (data.error) {
            setError(data.error);
          }
          
          // If we've reached a terminal state, stop polling
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(intervalId);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    // Initial check
    checkStatus();
    
    // Set up polling every 2 seconds
    intervalId = window.setInterval(checkStatus, 2000);
    
    // Clean up
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [taskId]);
  
  return { status, result, error, loading };
}
```

### 6. Handling Vercel Timeouts

Since our background task might reach Vercel's 60-second limit, we need a resilient approach:

1. **Idempotent Operations**: Make sure the concept generation step is idempotent, so if it fails and retries, it won't create duplicate data.

2. **Timeout Monitoring**: Add timeout detection in the background task:

```python
async def process_generation_task(...):
    start_time = time.time()
    
    try:
        # Update status to processing...
        
        # Check if we have enough time for the operation (allowing some buffer)
        if time.time() - start_time > 50:  # 50 seconds to be safe
            raise Exception("Function timeout imminent, need to restart")
            
        # Generate the concept...
        
        # Update database with successful result...
    except Exception as e:
        if "timeout imminent" in str(e):
            # Mark as still pending to be picked up by a cron job
            await db.execute(
                "UPDATE tasks SET status = :status, updated_at = :updated_at WHERE id = :id",
                {"id": task_id, "status": "pending", "updated_at": datetime.utcnow()}
            )
        else:
            # Handle normal errors...
```

3. **Cron Job for Cleanup**: Add a cron endpoint to handle tasks that timed out:

```python
@app.post("/api/cron/process-pending-tasks")
async def process_pending_tasks(
    db = Depends(get_db),
    service: ConceptService = Depends()
):
    """
    Cron job to process pending tasks that may have timed out.
    This should be called every minute from a Vercel cron job.
    """
    # Find tasks that have been in 'pending' status for more than 2 minutes
    stalled_tasks = await db.fetch_all(
        """
        SELECT id, session_id, request
        FROM tasks 
        WHERE status = 'pending' AND updated_at < :cutoff_time
        LIMIT 5  /* Process a few at a time */
        """,
        {"cutoff_time": datetime.utcnow() - timedelta(minutes=2)}
    )
    
    for task in stalled_tasks:
        # Start a new background task for each stalled task
        request_data = json.loads(task["request"])
        background_tasks.add_task(
            process_generation_task,
            task["id"],
            task["session_id"],
            request_data["logo_description"],
            request_data["theme_description"],
            service,
            db
        )
    
    return {"processed": len(stalled_tasks)}
```

### 7. Setting Up Vercel Cron

Create a Vercel configuration for the cron job in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/process-pending-tasks",
      "schedule": "* * * * *"  // Run every minute
    }
  ]
}
```

This implementation gives you a robust background task system that:
1. Immediately returns a task ID to the client
2. Processes generation in the background
3. Persists task state in Supabase
4. Provides a polling mechanism for clients to check status
5. Handles potential timeouts gracefully with a cron-based recovery process

All of this should work within Vercel's free tier constraints while providing a good user experience.

## FAQ

### Why use BackgroundTasks instead of Celery?

BackgroundTasks is a lightweight solution built into FastAPI that doesn't require additional infrastructure. For our modest requirements (< 20 users), this provides:

1. Simplicity - no additional services to set up and maintain
2. Cost efficiency - works within Vercel's free tier
3. Adequate functionality - handles our background processing needs

The trade-offs are:
- Limited to the lifetime of the serverless function (max 60 seconds on Vercel free tier)
- No persistent worker pool for high-volume background processing
- Less sophisticated task management compared to Celery

### Why not use Gunicorn with Uvicorn workers?

Gunicorn with Uvicorn workers is an excellent solution for traditional deployments that offers:
1. Multiple worker processes for true parallelism
2. Process management for stability
3. Graceful worker rotation and shutdown

However, in a serverless environment like Vercel:
1. You can't control the underlying server or process management
2. Serverless functions don't maintain long-running processes
3. Vercel automatically scales by creating new function instances

For self-hosted environments, the Gunicorn command would be:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```
Where:
- `-w 4` specifies 4 worker processes
- `-k uvicorn.workers.UvicornWorker` uses Uvicorn's ASGI workers
- This creates 4 parallel processes that can handle requests simultaneously

## Monitoring Considerations

To monitor the application performance:
- Use Vercel's built-in function metrics
- Implement logging to Vercel logs
- Add custom performance tracking in critical endpoints
- Consider implementing simple heartbeat checks 