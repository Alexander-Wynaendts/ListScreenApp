#!/bin/bash

# Create directories for Chrome and ChromeDriver
mkdir -p /opt/render/chrome

# Install dependencies
apt-get update && apt-get install -y wget unzip libnss3 libgconf-2-4 libxi6 libxcursor1 libxss1 libxrandr2 libatk1.0-0 libasound2 libpangocairo-1.0-0 fonts-liberation libappindicator3-1 xdg-utils libgbm1

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /opt/render/chrome/google-chrome-stable_current_amd64.deb
dpkg -i /opt/render/chrome/google-chrome-stable_current_amd64.deb || apt-get -f install -y

# Download ChromeDriver version matching Google Chrome's version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)
wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -O /opt/render/chrome/chromedriver_linux64.zip

# Unzip and set permissions
unzip /opt/render/chrome/chromedriver_linux64.zip -d /opt/render/chrome/
chmod +x /opt/render/chrome/chromedriver

# Check if ChromeDriver is installed correctly
if [ -f "/opt/render/chrome/chromedriver" ]; then
    echo "ChromeDriver installed successfully at /opt/render/chrome/chromedriver"
    /opt/render/chrome/chromedriver --version
else
    echo "Error: ChromeDriver installation failed."
fi

# Check Google Chrome installation
if command -v google-chrome > /dev/null 2>&1; then
    echo "Google Chrome installed successfully."
    google-chrome --version
else
    echo "Error: Google Chrome installation failed."
fi
