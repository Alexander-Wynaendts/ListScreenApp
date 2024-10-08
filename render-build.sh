#!/bin/bash

# Set the paths for Chrome and ChromeDriver
CHROME_PATH="/opt/render/chrome/google-chrome"
CHROMEDRIVER_PATH="/opt/render/chrome/chromedriver"

# Check if Chrome is installed
if [ ! -f "$CHROME_PATH" ]; then
  echo "Chrome not found. Installing Chrome..."

  # Create the directory for Chrome
  mkdir -p /opt/render/chrome/

  # Download Chrome
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb

  # Install Chrome
  sudo apt-get update
  sudo apt-get install -y /tmp/chrome.deb

  # Clean up
  rm /tmp/chrome.deb
else
  echo "Chrome already installed."
fi

# Check if ChromeDriver is installed
if [ ! -f "$CHROMEDRIVER_PATH" ]; then
  echo "ChromeDriver not found. Installing ChromeDriver..."

  # Get the version of Chrome
  CHROME_VERSION=$("$CHROME_PATH" --version | grep -oP '\d+\.\d+\.\d+')

  # Download the matching ChromeDriver version
  wget https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip -O /tmp/chromedriver.zip

  # Unzip ChromeDriver
  unzip /tmp/chromedriver.zip -d /opt/render/chrome/

  # Make ChromeDriver executable
  chmod +x /opt/render/chrome/chromedriver

  # Clean up
  rm /tmp/chromedriver.zip
else
  echo "ChromeDriver already installed."
fi

# Export the paths so they can be used by your Python scripts
export CHROME_PATH=$CHROME_PATH
export CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH

echo "Setup completed."
