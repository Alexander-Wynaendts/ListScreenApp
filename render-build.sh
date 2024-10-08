#!/usr/bin/env bash

# Create a directory for Chrome if it doesn't exist
mkdir -p ~/chrome

# Download and install Google Chrome (headless)
CHROME_VERSION="stable"
curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
dpkg -x google-chrome-${CHROME_VERSION}_current_amd64.deb ~/chrome

# Set the Chrome binary path
export PATH=$PATH:~/chrome/opt/google/chrome

# Download and install the correct ChromeDriver for the environment
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl -LO https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d ~/chrome
chmod +x ~/chrome/chromedriver

# Add ChromeDriver to the PATH
export PATH=$PATH:~/chrome

# Verify the installation of Google Chrome and ChromeDriver
google-chrome --version
chromedriver --version
