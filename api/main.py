from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from sandbox.manager import execute_code

app = FastAPI(title="Secure Python Code Executor")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecutionRequest(BaseModel):
    code: str


class ExecutionResponse(BaseModel):
    output: str = ""
    error: str = ""
    execution_time_ms: float


@app.post("/execute", response_model=ExecutionResponse)
async def execute(request: ExecutionRequest):
    """Execute user-submitted Python code in a secure Docker sandbox."""
    
    # Input validation: reject empty code
    if not request.code or request.code.strip() == "":
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    # Input validation: reject code longer than 2000 characters
    if len(request.code) > 2000:
        raise HTTPException(status_code=400, detail="Code exceeds maximum length of 2000 characters")
    
    try:
        # Execute code in sandbox and measure time
        start_time = time.time()
        stdout, stderr = execute_code(request.code)
        execution_time_ms = (time.time() - start_time) * 1000
        
        return ExecutionResponse(
            output=stdout,
            error=stderr,
            execution_time_ms=execution_time_ms
        )
    except Exception as e:
        # Never crash the server; return error to client
        return ExecutionResponse(
            output="",
            error=f"Execution error: {str(e)}",
            execution_time_ms=0
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
