#!/bin/bash

# Set executable permissions for the ChromeDriver
chmod +x script/chromedriver

# Test if the ChromeDriver is executable
if [ -x script/chromedriver ]; then
    echo "ChromeDriver is executable."
else
    echo "ChromeDriver is not executable."
fi

# Print the absolute path of ChromeDriver
absolute_path=$(realpath script/chromedriver)
echo "Absolute path: $absolute_path"
