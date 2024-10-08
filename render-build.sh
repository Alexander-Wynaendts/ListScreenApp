#!/usr/bin/env bash

# Create a directory for Chrome and ChromeDriver in /opt/render/chrome if it doesn't exist
mkdir -p /opt/render/chrome

# Download and install Google Chrome (headless) if not already present
if [ ! -f /opt/render/chrome/opt/google/chrome/chrome ]; then
    echo "Google Chrome not found. Downloading and installing Google Chrome..."
    CHROME_VERSION="stable"
    curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
    dpkg -x google-chrome-${CHROME_VERSION}_current_amd64.deb /opt/render/chrome
    echo "Google Chrome installed successfully."
else
    echo "Google Chrome is already installed."
fi

# Get the installed version of Google Chrome
CHROME_INSTALLED_VERSION=$(/opt/render/chrome/opt/google/chrome/chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')

# Download and install ChromeDriver if not already present
if [ ! -f /opt/render/chrome/chromedriver ]; then
    echo "ChromeDriver not found. Downloading and installing ChromeDriver..."
    CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_INSTALLED_VERSION%.*})
    curl -LO https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip -d /opt/render/chrome
    chmod +x /opt/render/chrome/chromedriver
    echo "ChromeDriver installed successfully for Chrome version ${CHROME_INSTALLED_VERSION}."
else
    echo "ChromeDriver is already installed."
fi

# Add Chrome and ChromeDriver to the PATH
export PATH=$PATH:/opt/render/chrome/opt/google/chrome
export PATH=$PATH:/opt/render/chrome

# Verify the installation of Google Chrome and ChromeDriver
if [ -f /opt/render/chrome/opt/google/chrome/chrome ]; then
    /opt/render/chrome/opt/google/chrome/chrome --version
else
    echo "Error: Google Chrome was not installed correctly."
    exit 1
fi

if [ -f /opt/render/chrome/chromedriver ]; then
    /opt/render/chrome/chromedriver --version
else
    echo "Error: ChromeDriver was not installed correctly."
    exit 1
fi

# Clean up the downloaded .deb and .zip files to save space
rm -f google-chrome-${CHROME_VERSION}_current_amd64.deb
rm -f chromedriver_linux64.zip

echo "Setup completed successfully."
