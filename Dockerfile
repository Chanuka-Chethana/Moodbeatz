# Use Python 3.9 as base
FROM python:3.9-slim

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Hugging Face Spaces defaults to port 7860
EXPOSE 7860

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
