#!/bin/bash

# Install dependencies for Chrome
sudo apt-get update
sudo apt-get install -y wget unzip

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# Download and install the correct ChromeDriver version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d{2,3}' | head -1)
DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d script
chmod +x script/chromedriver

# Print versions
google-chrome --version
script/chromedriver --version
