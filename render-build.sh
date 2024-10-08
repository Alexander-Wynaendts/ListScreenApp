#!/usr/bin/env bash

# Create a directory for Chrome if it doesn't exist
mkdir -p ~/chrome

# Download and install Google Chrome (headless)
CHROME_VERSION="stable"
curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
dpkg -x google-chrome-${CHROME_VERSION}_current_amd64.deb ~/chrome

# Set the Chrome binary path
export PATH=$PATH:~/chrome/opt/google/chrome

# Set the existing ChromeDriver path from the repository
chmod +x ./script/chromedriver
export PATH=$PATH:./script

# Verify the installation of Google Chrome and ChromeDriver
google-chrome --version
./script/chromedriver --version
