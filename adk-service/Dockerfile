FROM python:3.13-slim


WORKDIR /app

# Set environment variables
# Cloud Run will provide the PORT variable. Default to 8080 for local testing.
ENV PORT 8080
# These will be set in the Cloud Run service configuration for security
ENV DJANGO_API_URL=""
ENV ADK_WORKER_SECRET=""

# Copy the requirements file into the container
COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]