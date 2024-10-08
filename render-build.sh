#!/usr/bin/env bash

# Create a directory for Chrome and ChromeDriver in /opt/render/chrome if it doesn't exist
mkdir -p /opt/render/chrome

# Download and install Google Chrome (headless) if not already present
if [ ! -f /opt/render/chrome/opt/google/chrome/chrome ]; then
    echo "Google Chrome not found. Downloading and installing Google Chrome..."
    CHROME_VERSION="stable"
    curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
    dpkg -x google-chrome-${CHROME_VERSION}_current_amd64.deb /opt/render/chrome
else
    echo "Google Chrome is already installed."
fi

# Download and install ChromeDriver if not already present
if [ ! -f /opt/render/chrome/chromedriver ]; then
    echo "ChromeDriver not found. Downloading and installing ChromeDriver..."
    CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
    curl -LO https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip -d /opt/render/chrome
    chmod +x /opt/render/chrome/chromedriver
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
fi

if [ -f /opt/render/chrome/chromedriver ]; then
    /opt/render/chrome/chromedriver --version
else
    echo "Error: ChromeDriver was not installed correctly."
fi
