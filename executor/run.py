import os
import io
import contextlib

# Read Python code from environment variable
code = os.environ.get("USER_CODE", "")

# Capture stdout and stderr separately
stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

try:
    # Execute user code with captured stdout
    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
        exec(code)
    
    # Get captured output
    stdout_result = stdout_capture.getvalue()
    stderr_result = stderr_capture.getvalue()
    
except Exception as e:
    # Capture any execution errors
    stdout_result = ""
    stderr_result = str(e)

finally:
    # Print in exact format expected by manager.py
    print(f"STDOUT:{stdout_result}")
    print(f"STDERR:{stderr_result}")
