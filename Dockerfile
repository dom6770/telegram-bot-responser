# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy all required files
COPY ./src .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the data directory exists
RUN mkdir -p /usr/src/app/data
VOLUME /usr/src/app/data

# Run the application
CMD ["python", "./run.py"]
