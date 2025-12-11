FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Ensure data directory exists for SQLite
RUN mkdir -p data

# Run the scraper
CMD ["python", "main.py"]
