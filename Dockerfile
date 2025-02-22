# Use Python 3.11 slim as the base image.
FROM python:3.11-slim

# Prevent writing .pyc files and enable unbuffered output.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies.
#RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the dashboard application code.
COPY dashboard_app.py /app/dashboard_app.py
WORKDIR /app

# Expose the port the dashboard will run on.
EXPOSE 8050

# Run the dashboard application.
CMD ["python", "dashboard_app.py"]
