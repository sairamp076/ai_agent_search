# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing .pyc files to disc
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install any system dependencies (required for Django, no DB dependencies since using SQLite)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv (optional, if you are using pipenv)
RUN pip install --upgrade pip && pip install pipenv

# Copy the current directory contents into the container at /app
COPY . /app/

# Install the required Python packages using requirements.txt
RUN pip install -r requirements.txt

# Expose the port that Django will run on
EXPOSE 8000

# Set the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
