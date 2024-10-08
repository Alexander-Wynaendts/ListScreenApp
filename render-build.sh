#!/usr/bin/env bash

# Create a directory for Chrome and ChromeDriver in /opt/render/chrome if it doesn't exist
mkdir -p /opt/render/chrome

# Log the contents of the directory before starting (for debugging)
echo "Contents of /opt/render/chrome before installation:"
ls -la /opt/render/chrome

# Download and install Google Chrome (headless) if not already present
if [ ! -f /opt/render/chrome/opt/google/chrome/chrome ]; then
    echo "Google Chrome not found. Downloading and installing Google Chrome..."
    CHROME_VERSION="stable"
    curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
    dpkg -x google-chrome-${CHROME_VERSION}_current_amd64.deb /opt/render/chrome

    # Verify if the installation was successful
    if [ -f /opt/render/chrome/opt/google/chrome/chrome ]; then
        echo "Google Chrome installed successfully."
    else
        echo "Error: Failed to install Google Chrome."
    fi
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

    # Verify if the installation was successful
    if [ -f /opt/render/chrome/chromedriver ]; then
        echo "ChromeDriver installed successfully."
    else
        echo "Error: Failed to install ChromeDriver."
    fi
else
    echo "ChromeDriver is already installed."
fi

# Add Chrome and ChromeDriver to the PATH
export PATH=$PATH:/opt/render/chrome/opt/google/chrome
export PATH=$PATH:/opt/render/chrome

# Log the current PATH (for debugging)
echo "Current PATH: $PATH"

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

# Log the contents of the directory after installation (for debugging)
echo "Contents of /opt/render/chrome after installation:"
ls -la /opt/render/chrome
