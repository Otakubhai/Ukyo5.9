# Base image with Python
FROM python:3.11-slim

# Set working dir inside container
WORKDIR /app

# Install system dependencies (for pyrogram, pillow, etc.)
RUN apt update && apt install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to cache layers
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Now copy rest of the code
COPY . .

# If you use .env, install dotenv
RUN pip install python-dotenv

# Run the bot (you can change this to another file if entry is different)
CMD ["python", "merged_bot.py"]
