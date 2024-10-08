#!/bin/bash

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Set executable permissions for ChromeDriver
chmod +x script/chromedriver

# Check Chrome and ChromeDriver versions
google-chrome --version
script/chromedriver --version
