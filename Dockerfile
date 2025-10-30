FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment outside of /app (so bind mounts don't overwrite it)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Install Python dependencies into the /opt/venv environment
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# Expose port
EXPOSE 8000

# Run the application using Python from the venv
CMD ["python", "run.py"]
