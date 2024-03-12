# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Make a directory for our application
WORKDIR /usr/src/app

# Install the requirements
COPY flask-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory into the Docker image
COPY flask-app /usr/src/app

# Set the environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run"]