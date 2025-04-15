# Base image with Python
FROM python:3.11-slim

# Set working dir inside container
WORKDIR /app

# Install system dependencies (for pyrogram, pillow, ffmpeg, etc.)
RUN apt update && apt install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY . .

# (Optional) Install dotenv if you're using .env files
RUN pip install python-dotenv

# Set environment variables from .env file (if used)
ENV PYTHONUNBUFFERED=1

# Start the bot
CMD ["python", "merged_bot.py"]
