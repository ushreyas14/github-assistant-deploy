# Hugging Face Spaces requires port 7860
FROM python:3.12-slim

# Install git — required by GitPython to clone repositories
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project source
COPY . .

# Create the repos directory where cloned repositories will be stored
RUN mkdir -p repos

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Run the FastAPI backend on port 7860
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
