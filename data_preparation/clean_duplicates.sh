#!/bin/bash

# Directory containing the audio files
INPUT_DIR="/scratch1/data/raw_data/CLEAR_ASR/IN_PREP/downloaded_corpora"

# Function to convert single file
convert_audio() {
    local input="$1"
    local temp="${input%.*}.temp.wav"
    
    echo "Converting: $input"
    
    # Try conversion
    if ffmpeg -i "$input" -acodec pcm_s16le -ac 1 -ar 16000 "$temp" -y -loglevel error; then
        # Only replace original if conversion succeeded
        if mv "$temp" "$input"; then
            echo "✓ Done"
            return 0
        else
            echo "✗ Failed to replace original file"
            rm -f "$temp"  # Clean up temp file
            echo "$input" >> failed_conversions.txt
            return 1
        fi
    else
        echo "✗ Failed to convert"
        rm -f "$temp"  # Clean up temp file
        echo "$input" >> failed_conversions.txt
        return 1
    fi
}

# Initialize/clear failed conversions log
echo "Starting conversion at $(date)" > failed_conversions.txt

# Process each file individually
find "$INPUT_DIR" -type f \( -name "*.wav" -o -name "*.mp3" \) -exec bash -c 'convert_audio "$0"' {} \;

# Report summary
echo "Conversion complete"
echo "Failed conversions (if any) are logged in failed_conversions.txt"
if [ -s failed_conversions.txt ]; then
    echo "The following files failed:"
    cat failed_conversions.txt
fi
