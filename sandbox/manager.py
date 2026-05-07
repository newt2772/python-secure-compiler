import docker
import os
import time

# Initialize Docker client
client = docker.from_env()


def execute_code(code: str, timeout: int = 5) -> tuple:
    """
    Execute Python code in a secure Docker container.
    
    Args:
        code: Python code string to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        tuple: (stdout, stderr) output from the code execution
    """
    
    container = None
    start_time = time.time()
    
    try:
        # Start Docker container with strict security constraints
        container = client.containers.run(
            image="python:3.11-alpine",
            
            # Prevents container from accessing network services
            network_mode="none",
            
            # Limits memory usage to prevent DoS attacks
            mem_limit="128m",
            
            # Limits CPU usage to prevent resource exhaustion
            cpuset_cpus="0",
            cpu_quota=50000,
            cpu_period=100000,
            
            # Read-only filesystem prevents persistence of malicious code
            read_only=True,
            
            # Prevents container from gaining new privileges
            security_opt=["no-new-privileges"],
            
            # Run as non-root user to limit damage from privilege escalation
            user="nobody",
            
            # Limits number of processes to prevent fork bombs
            pids_limit=32,
            
            # Auto-remove container after execution to free resources
            remove=True,
            
            # Pass user code as environment variable
            environment={"USER_CODE": code},
            
            # Volume mount for executor script
            volumes={
                os.path.abspath("executor"): {"bind": "/app", "mode": "ro"}
            },
            
            # Working directory where executor runs
            working_dir="/app",
            
            # Execute the run script
            command=["python", "run.py"],
            
            # Capture stdout and stderr
            stdout=True,
            stderr=True,
            
            # Do not detach; wait for container to finish
            detach=True,
        )
        
        # Wait for container with timeout
        try:
            exit_code = container.wait(timeout=timeout)
        except docker.errors.APIError:
            # Timeout occurred; kill the container
            container.kill()
            return "", "Execution timed out"
        
        # Get logs from container
        logs = container.logs(stdout=True, stderr=True).decode('utf-8', errors='replace')
        
        # Parse output in format: STDOUT:<output>\nSTDERR:<output>
        stdout = ""
        stderr = ""
        
        if "STDOUT:" in logs and "STDERR:" in logs:
            parts = logs.split("\nSTDERR:")
            stdout = parts[0].replace("STDOUT:", "", 1).strip()
            stderr = parts[1].strip() if len(parts) > 1 else ""
        elif "STDOUT:" in logs:
            stdout = logs.replace("STDOUT:", "", 1).strip()
        elif "STDERR:" in logs:
            stderr = logs.replace("STDERR:", "", 1).strip()
        else:
            stdout = logs
        
        return stdout, stderr
        
    except docker.errors.ImageNotFound:
        return "", "Docker image python:3.11-alpine not found. Please build the image first."
    except Exception as e:
        return "", f"Error: {str(e)}"
    finally:
        # Ensure container is cleaned up
        if container:
            try:
                container.kill()
            except:
                pass
            try:
                container.remove()
            except:
                pass
