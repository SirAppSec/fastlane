#!/bin/bash

# Load configuration from config.yml
CONFIG_FILE="../config.yml"
eval "$(sed -n 's/^docker:/docker_/p' $CONFIG_FILE)"

# SSH into the remote server and deploy the Docker container
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << EOF
  # Pull the Docker image
  docker pull $docker_registry_url/$docker_image_name:$docker_image_tag

  # Stop and remove the existing container (if any)
  docker stop fastlane-scraper || true
  docker rm fastlane-scraper || true

  # Run the new container
  docker run -d \
    --name fastlane-scraper \
    -p 5000:5000 \
    $docker_registry_url/$docker_image_name:$docker_image_tag
EOF
