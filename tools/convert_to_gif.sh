#!/bin/bash

# Help function
function show_help() {
  echo "Usage: $0 <input_video>"
  echo
  echo "This script converts a video file to a GIF with the following properties:"
  echo "  - Frame rate: 10 fps"
  echo "  - Resolution: 1728x1028 (with padding if needed)"
  echo
  echo "Example:"
  echo "  $0 input.mov"
  echo
  echo "The output file will be named 'output.gif'."
}

# Check if help is requested
if [[ "$1" == "-h" || "$1" == "--h" || "$1" == "-help" || "$1" == "--help" ]]; then
  show_help
  exit 0
fi

# Check if the input file is provided
if [ "$#" -ne 1 ]; then
  echo "Error: Missing input file."
  echo "Use --help for usage information."
  exit 1
fi

# Input video file
input_file="$1"
output_file="output.gif"

# Conversion parameters
fps=10
width=1728
height=1028

# Convert the video to GIF
ffmpeg -i "$input_file" -vf "fps=$fps,scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2" "$output_file"

echo "Conversion complete! Output file: $output_file"

