# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    libnss3 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    fonts-liberation \
    libasound2 \
    xdg-utils \
    libgtk-3-0

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver matching the Chrome version
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d{2,3}' | head -1) && \
    DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set environment variables
ENV PATH="$PATH:/usr/local/bin:/opt/google/chrome"

# Copy your app code into the Docker image
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (if necessary)
EXPOSE 5000

# Run the app (adjust to how you run the app, e.g., flask, fastapi, etc.)
CMD ["python", "app.py"]
