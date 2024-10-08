#!/bin/bash

# Set the paths for Chrome and ChromeDriver
CHROME_PATH="/opt/render/chrome/google-chrome"
CHROMEDRIVER_PATH="/opt/render/chrome/chromedriver"
CHROME_VERSION_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
CHROMEDRIVER_VERSION_URL="https://chromedriver.storage.googleapis.com"

# Create necessary directories
mkdir -p /opt/render/chrome/

# Check if Chrome is installed
if [ ! -f "$CHROME_PATH" ]; then
  echo "Chrome not found. Installing Chrome..."

  # Download and install Chrome
  wget $CHROME_VERSION_URL -O /tmp/chrome.deb
  apt-get update
  apt-get install -y /tmp/chrome.deb --no-install-recommends

  # Clean up
  rm /tmp/chrome.deb
else
  echo "Chrome already installed."
fi

# Get the Chrome version to download matching ChromeDriver
if [ -f "$CHROME_PATH" ]; then
  CHROME_VERSION=$("$CHROME_PATH" --version | grep -oP '\d+\.\d+\.\d+' | head -1)
else
  echo "Error: Chrome was not installed correctly."
  exit 1
fi

# Check if ChromeDriver is installed
if [ ! -f "$CHROMEDRIVER_PATH" ]; then
  echo "ChromeDriver not found. Installing ChromeDriver..."

  # Fetch the correct ChromeDriver version
  CHROMEDRIVER_DOWNLOAD_URL="$CHROMEDRIVER_VERSION_URL/$CHROME_VERSION/chromedriver_linux64.zip"
  wget $CHROMEDRIVER_DOWNLOAD_URL -O /tmp/chromedriver.zip

  # Check if the file was downloaded successfully
  if [ $? -eq 0 ]; then
    # Unzip ChromeDriver
    unzip /tmp/chromedriver.zip -d /opt/render/chrome/
    chmod +x /opt/render/chrome/chromedriver

    # Clean up
    rm /tmp/chromedriver.zip
  else
    echo "Error: ChromeDriver version $CHROME_VERSION not found."
    exit 1
  fi
else
  echo "ChromeDriver already installed."
fi

# Export the paths so they can be used by your Python scripts
export CHROME_PATH=$CHROME_PATH
export CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH

echo "Setup completed."
