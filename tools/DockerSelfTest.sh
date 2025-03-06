#!/bin/bash

# Capture parameters for the command to run
CMD_TO_RUN="$@"

# Execute the command and capture its output and exit status
OUTPUT=$($CMD_TO_RUN 2>&1)
EXIT_STATUS=$?

# Print the command output before determining success or failure
echo "$OUTPUT"

# If the command includes --help, we only care if it runs successfully
if [[ "$CMD_TO_RUN" == *"--help"* ]]; then
    if [ $EXIT_STATUS -ne 0 ]; then
        echo "FAIL"
    else
        echo "SUCCESS"
    fi
    exit 0
fi

# Check if the command failed
if [ $EXIT_STATUS -ne 0 ]; then
    echo "FAIL"
    exit 0
fi

# Check for .m4b files in the audiobooks directory
CHECK_FOLDER="audiobooks"
M4B_FILE=$(find "$CHECK_FOLDER" -type f -name "*.m4b" | head -n 1)

if [ -z "$M4B_FILE" ]; then
    echo "FAIL"
    exit 0
fi

# Check if the found .m4b file is empty
if [ ! -s "$M4B_FILE" ]; then
    echo "FAIL"
    exit 0
fi

# If everything is fine, print success
echo "SUCCESS"

# Remove specific directories inside audiobooks
rm -rf "$CHECK_FOLDER"/cli "$CHECK_FOLDER"/gui/host "$CHECK_FOLDER"/gui/gradio

exit 0

