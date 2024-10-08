# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y wget unzip curl

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm ./google-chrome-stable_current_amd64.deb

# Set the Chrome binary location for Selenium
ENV CHROME_BIN=/usr/bin/google-chrome

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run your application
CMD ["python", "app.py"]


