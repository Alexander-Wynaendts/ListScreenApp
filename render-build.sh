#!/bin/bash

# Install Google Chrome manually
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb /tmp/google-chrome
export PATH=/tmp/google-chrome/opt/google/chrome:$PATH

# Get Chrome version and download the matching ChromeDriver
CHROME_VERSION=$(/tmp/google-chrome/opt/google/chrome/google-chrome --version | grep -oP '\d{2,3}' | head -1)
DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d script
chmod +x script/chromedriver

# Print versions
/tmp/google-chrome/opt/google/chrome/google-chrome --version
script/chromedriver --version
