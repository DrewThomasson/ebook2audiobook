#!/bin/bash

# Run the Docker command and pass all arguments as a single command
DOCKER_LOG=$(docker run --rm --pull=always \
    athomasson2/ebook2audiobook:latest \
    /bin/bash -c "$*" 2>&1)

# Print the full log
echo "$DOCKER_LOG"

# Determine the outcome
if echo "$DOCKER_LOG" | grep -q "SUCCESS"; then
    echo "SUCCESS"
    exit 0
elif echo "$DOCKER_LOG" | grep -q "FAIL"; then
    echo "FAIL"
    exit 1
else
    echo "FAIL"
    exit 1
fi
