FROM python:3.12-slim

# Install system libs for PyMySQL (pure Python, so this is light)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

# Health check for ALB target group
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost/health || exit 1

EXPOSE 80
CMD ["python", "app.py"]
