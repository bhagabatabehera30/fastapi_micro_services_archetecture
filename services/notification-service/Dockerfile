FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/notification-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared package
COPY packages/ /app/packages/
RUN pip install -e /app/packages/shared

# Copy service code
COPY services/notification-service /app/services/notification-service

ENV PYTHONPATH=/app
WORKDIR /app/services/notification-service

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
