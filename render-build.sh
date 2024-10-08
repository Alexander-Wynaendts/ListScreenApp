#!/bin/bash

# Set paths for Chrome and ChromeDriver
CHROME_PATH="/opt/render/chrome/google-chrome"
CHROMEDRIVER_PATH="/opt/render/chrome/chromedriver"
CHROME_VERSION_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
CHROMEDRIVER_VERSION_URL="https://chromedriver.storage.googleapis.com"

# Create necessary directories
mkdir -p /opt/render/chrome/

# Download and extract Chrome without using apt-get
if [ ! -f "$CHROME_PATH" ]; then
  echo "Chrome not found. Downloading and installing Chrome..."

  # Download Chrome
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -O /opt/render/chrome/google-chrome.rpm

  # Extract Chrome (using RPM tool to manually install it)
  rpm2cpio /opt/render/chrome/google-chrome.rpm | cpio -idmv -D /opt/render/chrome/
  chmod +x /opt/render/chrome/google-chrome

  # Cleanup
  rm /opt/render/chrome/google-chrome.rpm
else
  echo "Chrome already installed at $CHROME_PATH."
fi

# Get the Chrome version to download the matching ChromeDriver
if [ -f "$CHROME_PATH" ]; then
  CHROME_VERSION=$("$CHROME_PATH" --version | grep -oP '\d+\.\d+\.\d+' | head -1)
else
  echo "Error: Chrome was not installed correctly."
  exit 1
fi

# Check if ChromeDriver is installed
if [ ! -f "$CHROMEDRIVER_PATH" ]; then
  echo "ChromeDriver not found. Installing ChromeDriver..."

  # Download ChromeDriver matching the Chrome version
  CHROMEDRIVER_DOWNLOAD_URL="$CHROMEDRIVER_VERSION_URL/$CHROME_VERSION/chromedriver_linux64.zip"
  wget $CHROMEDRIVER_DOWNLOAD_URL -O /tmp/chromedriver.zip

  if [ $? -eq 0 ]; then
    # Unzip ChromeDriver
    unzip /tmp/chromedriver.zip -d /opt/render/chrome/
    chmod +x /opt/render/chrome/chromedriver

    # Cleanup
    rm /tmp/chromedriver.zip
  else
    echo "Error: ChromeDriver version $CHROME_VERSION not found."
    exit 1
  fi
else
  echo "ChromeDriver already installed at $CHROMEDRIVER_PATH."
fi

# Verify installation by printing the paths
echo "ChromeDriver Path: $CHROMEDRIVER_PATH"
echo "Chrome Path: $CHROME_PATH"

# Export the paths so they can be used by Python scripts
export CHROME_PATH=$CHROME_PATH
export CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH

echo "Setup completed."
