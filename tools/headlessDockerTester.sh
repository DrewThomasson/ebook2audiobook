#!/bin/bash

# Move the script to the current directory in the workflow please or it won't be able to find the script
# mv tools/headlessDockerTester.sh headlessDockerTester.sh 2>/dev/null

# Ensure required directories exist
mkdir -p workflow-testing audiobooks

# Capture parameters for Docker command
DOCKER_PARAMS="$@"

# Run the Docker command and capture logs
DOCKER_LOG=$(docker run --rm \
    -v "$(pwd)/workflow-testing:/home/user/app/workflow-testing" \
    -v "$(pwd)/audiobooks:/home/user/app/audiobooks" \
    athomasson2/ebook2audiobook \
    $DOCKER_PARAMS 2>&1)

# Check if the Docker command was successful
if [ $? -ne 0 ]; then
    echo "Docker command failed!"
    echo "$DOCKER_LOG"
    exit 1
fi

# Check for m4b files in the audiobooks directory
M4B_FILE=$(find audiobooks -type f -name "*.m4b" | head -n 1)

if [ -z "$M4B_FILE" ]; then
    echo "No .m4b file found! Process failed!"
    echo "$DOCKER_LOG"
    exit 1
fi

# Check if the found m4b file is empty
if [ ! -s "$M4B_FILE" ]; then
    echo "The .m4b file is empty! Process failed!"
    echo "$DOCKER_LOG"
    exit 1
fi

# If everything is fine, clean up the specified directories
rm -rf audiobooks/cli audiobooks/gui/host audiobooks/gui/gradio

echo "Test passed successfully!"
exit 0
