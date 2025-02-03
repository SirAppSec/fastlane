#!/bin/bash
import sys

# Set the PYTHONPATH to the project root directory
export PYTHONPATH=$(pwd)

CONFIG_FILE="../config.yml"
eval "$(sed -n 's/^testing:/testing_/p' $CONFIG_FILE)"

# Run flake8 for linting
pytest $linting_flake8_config $test_location
