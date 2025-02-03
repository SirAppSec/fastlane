#!/bin/bash

# Load configuration from config.yml
CONFIG_FILE="../config.yml"
eval "$(sed -n 's/^docker:/docker_/p' $CONFIG_FILE)"

# Build Docker image
docker build -t $docker_image_name:$docker_image_tag ..

# Log in to Docker registry
echo "$docker_password" | docker login -u "$docker_username" --password-stdin $docker_registry_url

# Tag and push Docker image
docker tag $docker_image_name:$docker_image_tag $docker_registry_url/$docker_image_name:$docker_image_tag
docker push $docker_registry_url/$docker_image_name:$docker_image_tag

# Log out from Docker registry
docker logout $docker_registry_url
