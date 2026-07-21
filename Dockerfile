# Multi-stage build
FROM python:3.9-slim as builder

WORKDIR /app

# Build dependencies install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Python dependencies copy karein
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Application copy karein
COPY gitlab.py .

# Non-root user create karein
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Port expose karein
EXPOSE 5000

# Application run karein
CMD ["python", "gitlab.py"]
