#!/bin/bash

# Create directories for Chrome and ChromeDriver
mkdir -p /opt/render/chrome

# Install dependencies
apt-get update && apt-get install -y wget unzip libnss3 libgconf-2-4 libxi6 libxcursor1 libxss1 libxrandr2 libatk1.0-0 libasound2 libpangocairo-1.0-0 fonts-liberation libappindicator3-1 xdg-utils libgbm1 || echo "Some dependencies could not be installed, proceeding..."

# Download and install Google Chrome manually
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /opt/render/chrome/google-chrome-stable_current_amd64.deb

# Unpack Chrome instead of using dpkg (since superuser access is not available)
dpkg-deb -x /opt/render/chrome/google-chrome-stable_current_amd64.deb /opt/render/chrome/

# Set Chrome binary path in the environment variable for future use
export PATH="/opt/render/chrome/opt/google/chrome:$PATH"

# Verify Chrome installation
if [ -f "/opt/render/chrome/opt/google/chrome/chrome" ]; then
    echo "Google Chrome installed successfully."
    /opt/render/chrome/opt/google/chrome/chrome --version
else
    echo "Error: Google Chrome installation failed."
fi

# Get the exact Chrome version
CHROME_VERSION=$(/opt/render/chrome/opt/google/chrome/chrome --version | grep -oP '\d+\.\d+\.\d+' | head -1)

# Try to fetch the corresponding ChromeDriver version for the installed Chrome
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# If the exact version cannot be found, use the latest stable ChromeDriver version
if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Unable to find ChromeDriver for Chrome version $CHROME_VERSION. Falling back to the latest ChromeDriver version."
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
fi

# Download ChromeDriver
wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -O /opt/render/chrome/chromedriver_linux64.zip

# Unzip ChromeDriver
unzip /opt/render/chrome/chromedriver_linux64.zip -d /opt/render/chrome/
chmod +x /opt/render/chrome/chromedriver

# Verify ChromeDriver installation
if [ -f "/opt/render/chrome/chromedriver" ]; then
    echo "ChromeDriver installed successfully at /opt/render/chrome/chromedriver"
    /opt/render/chrome/chromedriver --version
else
    echo "Error: ChromeDriver installation failed."
fi
