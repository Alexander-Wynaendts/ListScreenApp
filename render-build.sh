#!/usr/bin/env bash

# Mettre à jour les paquets
apt-get update

# Installer les dépendances requises
apt-get install -y curl unzip

# Télécharger et installer Google Chrome stable
CHROME_VERSION="stable"
curl -LO https://dl.google.com/linux/direct/google-chrome-${CHROME_VERSION}_current_amd64.deb
dpkg -i google-chrome-${CHROME_VERSION}_current_amd64.deb || apt-get -fy install

# Vérifier l'installation de Chrome
google-chrome --version

# Télécharger et installer ChromeDriver correspondant à la version de Chrome
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl -LO https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Vérifier l'installation de ChromeDriver
chromedriver --version
