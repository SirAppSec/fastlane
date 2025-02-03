#!/bin/bash

# Load configuration from config.yml
CONFIG_FILE="../config.yml"
FLASK_HOST=$(yq e '.flask.host' $CONFIG_FILE)
FLASK_PORT=$(yq e '.flask.port' $CONFIG_FILE)

# SSH into the remote server and deploy the application
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << EOF
  # Create a directory for the application
  mkdir -p /opt/fastlane-scraper

  # Copy the application files
  rsync -avz --exclude='venv/' --exclude='.git/' --exclude='.env' ./ $SSH_USER@$SSH_HOST:/opt/fastlane-scraper

  # Install dependencies
  python3 -m venv /opt/fastlane-scraper/venv
  source /opt/fastlane-scraper/venv/bin/activate
  pip install -r /opt/fastlane-scraper/requirements.txt

  # Stop the existing application (if running)
  pkill -f "python main.py" || true

  # Start the application
  nohup python3 /opt/fastlane-scraper/main.py > /opt/fastlane-scraper/app.log 2>&1 &
EOF
