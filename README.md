# python-secure-compiler
# Secure Python Code Execution Engine

A web application that safely executes Python code in isolated Docker sandboxes with strict security constraints. Submit Python code through a clean web interface and receive results instantly.

## Features

- 🐳 **Docker Sandbox**: Code runs in isolated containers
- 🔒 **Security First**: Network disabled, read-only filesystem, non-root user
- ⚡ **Resource Limited**: Memory, CPU, and process count restrictions
- 🎨 **Clean UI**: Dark-themed interface with real-time output
- 🚀 **Fast Execution**: Sub-second code execution
- 📊 **Execution Time Tracking**: Shows millisecond-level timing

## Prerequisites

- Docker (with Docker daemon running)
- Python 3.11+
- pip (Python package manager)

## Setup Instructions

### 1. Build the Docker Image

```bash
docker build -t py-executor:latest .
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with docker-compose:

```bash
docker-compose up -d
```

### 4. Open the Frontend

Open `frontend/index.html` in your web browser:

```bash
# On Windows
start frontend/index.html

# On macOS
open frontend/index.html

# On Linux
xdg-open frontend/index.html
```

Or navigate to: `file:///path/to/frontend/index.html`

Access the API at: `http://localhost:8000`

## How It Works

1. **User submits code** through the web interface
2. **FastAPI validates** the code (non-empty, ≤2000 characters)
3. **Docker container spawns** with strict security constraints
4. **Code executes** inside the isolated container using Python's `exec()`
5. **Output captured** and returned to the frontend
6. **Container auto-removes** to free resources

## Architecture

```
Frontend (HTML/JS)
       ↓ (fetch POST)
FastAPI Server (api/main.py)
       ↓ (Docker SDK)
Docker Container (executor/run.py)
       ↓ (exec())
User Code
```

## API Endpoints

### POST /execute
Execute Python code in a sandbox.

**Request:**
```json
{
  "code": "print('Hello, World!')"
}
```

**Response:**
```json
{
  "output": "Hello, World!\n",
  "error": "",
  "execution_time_ms": 245.5
}
```

**Status Codes:**
- `200 OK`: Code executed (may have errors in stderr)
- `400 Bad Request`: Invalid input (empty or too long)
- `500 Internal Server Error`: Server error

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Security Layers

### 1. **Network Isolation**
- `network_mode="none"`: Container has no network access
- Prevents exfiltration of data

### 2. **Filesystem Protection**
- `read_only=True`: Filesystem is read-only
- Prevents writing malicious files to disk

### 3. **Resource Limits**
- Memory: 128MB (prevents memory exhaustion)
- CPU: 0.5 CPUs (prevents CPU starvation)
- Processes: 32 max (prevents fork bombs)

### 4. **User Isolation**
- `user="nobody"`: Runs as non-root user
- Limits damage from privilege escalation exploits

### 5. **Privilege Restriction**
- `security_opt=["no-new-privileges"]`: Cannot gain new capabilities
- Prevents capability escalation attacks

### 6. **Execution Timeout**
- 5-second timeout: Kills runaway processes
- Prevents infinite loops from blocking server

### 7. **Input Validation**
- Max code length: 2000 characters
- Rejects empty submissions

### 8. **Seccomp Filtering** (in seccomp.json)
- Blocks dangerous syscalls: `socket`, `fork`, `clone`, `ptrace`, `mount`, etc.
- Whitelist-based approach for additional hardening

## Project Structure

```
project/
├── api/
│   └── main.py              # FastAPI server with /execute endpoint
├── sandbox/
│   ├── manager.py           # Docker container orchestration
│   └── seccomp.json         # Seccomp profile for syscall filtering
├── executor/
│   └── run.py               # Script that runs inside container
├── frontend/
│   └── index.html           # Web UI (HTML/CSS/JS)
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-container orchestration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Example Usage

### 1. Simple Print
```python
print("Hello, Secure Sandbox!")
```

### 2. Math Operations
```python
x = 25
y = 15
print(f"Addition: {x + y}")
print(f"Multiplication: {x * y}")
```

### 3. List Comprehension
```python
squares = [x**2 for x in range(10)]
print(squares)
```

### 4. Error Handling
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error caught: {e}")
```

## Limitations

- **No imports allowed**: Dangerous modules are restricted
- **No network access**: Container network disabled
- **No file I/O**: Read-only filesystem
- **Limited execution time**: 5-second timeout
- **Limited resources**: 128MB RAM, 0.5 CPUs
- **Maximum code length**: 2000 characters

## Troubleshooting

### Docker Image Not Found
```
Error: Docker image python:3.11-alpine not found
```
**Solution**: Run `docker build -t py-executor:latest .`

### Connection Refused
```
Error: Cannot connect to localhost:8000
```
**Solution**: Ensure FastAPI server is running with `uvicorn api.main:app --host 0.0.0.0 --port 8000`

### Docker Daemon Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution**: Start Docker Desktop or Docker daemon

### CORS Errors
```
Access to fetch has been blocked by CORS policy
```
**Solution**: The server includes CORS middleware. Ensure you're accessing from `file://` or `http://localhost`

## Performance Notes

- Typical execution: 200-500ms (includes Docker startup overhead)
- Container startup: ~100-150ms
- Code execution: <50ms for simple operations
- Auto-cleanup: Minimal resource footprint

## Future Enhancements

- [ ] Support for additional languages (JavaScript, Go, Rust)
- [ ] Code syntax highlighting in editor
- [ ] Execution history
- [ ] Output download as file
- [ ] Rate limiting per IP
- [ ] Custom execution timeout input
- [ ] Preset code examples

## License

Open source - feel free to modify and distribute

## Security Disclaimer

While this application implements multiple security layers, **executing arbitrary user code always carries inherent risks**. Use in trusted environments only. This is designed for educational purposes and controlled environments.
