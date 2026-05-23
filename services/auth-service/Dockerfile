FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/auth-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared package and install it locally
COPY packages/ /app/packages/
RUN pip install -e /app/packages/shared

# Copy the actual service code
COPY services/auth-service /app/services/auth-service

# Set pythonpath
ENV PYTHONPATH=/app
WORKDIR /app/services/auth-service

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
