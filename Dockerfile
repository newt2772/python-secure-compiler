FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy executor script into the image
COPY executor/run.py /app/run.py

# Default command to run executor
CMD ["python", "run.py"]
