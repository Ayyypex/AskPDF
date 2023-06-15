#!/bin/bash

# Ensure pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip not found. Please make sure pip is installed."
    exit 1
fi

# Path to the requirements.txt file
REQUIREMENTS_FILE="../docker/requirements.txt"

# Check if requirements.txt file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "requirements.txt file not found."
    exit 1
fi

# Install requirements
pip install -r "$REQUIREMENTS_FILE"

# Check the exit code of the pip command
if [ $? -eq 0 ]; then
    echo "Requirements installed successfully."
else
    echo "Failed to install requirements."
fi