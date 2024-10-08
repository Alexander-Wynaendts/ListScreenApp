#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

# Download Chrome if not cached
if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src
else
  echo "...Using Chrome from cache"
fi

# Install ChromeDriver
CHROME_VERSION=$($STORAGE_DIR/chrome/opt/google/chrome/google-chrome --version | grep -oP '\d{2,3}' | head -1)
DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d script
chmod +x script/chromedriver

# Print versions
$STORAGE_DIR/chrome/opt/google/chrome/google-chrome --version
script/chromedriver --version
