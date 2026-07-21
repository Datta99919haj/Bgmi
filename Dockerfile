FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify installation (important!)
RUN python -c "import gitlab; print('✅ GitLab module found!')"

# Copy your code
COPY gitlab.py .

# Run
CMD ["python", "gitlab.py"]
