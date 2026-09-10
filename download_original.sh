#!/usr/bin/env bash
#
# download.sh — downloads split archive parts, merges them, and checks md5.
# Just edit the constants below and run: ./download.sh

set -euo pipefail

BASE_URL="https://cognitive-ml.fr/downloads/tinyVox"
FILENAME="tinyVox.original.tar.gz"
OUTPUT_DIR="./tinyVox"
PART_COUNT=6
EXPECTED_MD5="ebde0b7933c602426c19b210c1ada4d7"

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

chars=({a..z})
for i in $(seq 0 $((PART_COUNT - 1))); do
    suffix="${chars[$(( i / 26 ))]}${chars[$(( i % 26 ))]}"
    part="${FILENAME}.part-${suffix}"
    echo "Downloading ${part}..."
    curl -fSL -o "$part" "${BASE_URL}/${part}"
done

echo "Merging parts into ${FILENAME}..."
cat "${FILENAME}".part-* > "$FILENAME"

echo "Verifying checksum..."
actual_md5="$(md5sum "$FILENAME" | awk '{print $1}')"

if [[ "$actual_md5" == "$EXPECTED_MD5" ]]; then
    echo "OK: ${FILENAME} reassembled and verified successfully."
else
    echo "ERROR: checksum mismatch (expected $EXPECTED_MD5, got $actual_md5)" >&2
    exit 1
fi

