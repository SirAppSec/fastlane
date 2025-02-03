#!/bin/bash

# Load configuration from config.yml
CONFIG_FILE="../config.yml"
eval "$(sed -n 's/^linting:/linting_/p' $CONFIG_FILE)"

# Run flake8 for linting
flake8 --config=$linting_flake8_config ..

# Run autopep8 for auto-fixing
autopep8 $linting_autopep8_config --recursive ..
