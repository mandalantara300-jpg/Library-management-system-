# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Copy application files
COPY . .

# Initialize the 500-book database
RUN python3 seed_500_books.py

# Expose server port
EXPOSE 8000

# Run the CampusShelf server
CMD ["python3", "web_app.py"]
