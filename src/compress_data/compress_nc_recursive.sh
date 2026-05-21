#!/bin/bash
# Recursively compress all NetCDF files under a given path to NetCDF4 zip.
# Usage: ./compress_nc_recursive.sh /path/to/search

set -euo pipefail

# Function to show usage
usage() {
    echo "Usage: $0 <directory> [--replace]"
    echo "  <directory> : root directory to search for .nc files"
    echo "  --replace   : (optional) replace original files (otherwise creates *_compressed.nc)"
    exit 1
}

# Parse arguments
if [ $# -lt 1 ]; then
    usage
fi

SEARCH_DIR="$1"
REPLACE=false

if [ $# -eq 2 ] && [ "$2" = "--replace" ]; then
    REPLACE=true
fi

# Check if directory exists
if [ ! -d "$SEARCH_DIR" ]; then
    echo "Error: Directory '$SEARCH_DIR' does not exist."
    exit 1
fi

# Set compression parameters
COMPRESSION="zip_5"   # adjust level: zip_1 .. zip_9
FORMAT="nc4"

# Use nccopy if available (faster), otherwise fallback to cdo
if command -v nccopy &>/dev/null; then
    USE_NCCOPY=true
    echo "Using nccopy for compression."
else
    USE_NCCOPY=false
    echo "nccopy not found, using cdo instead."
fi

# Find all .nc files
find "$SEARCH_DIR" -type f -name "*.nc" -print0 | while IFS= read -r -d '' file; do
    if $REPLACE; then
        # Replace original: create temporary, then move
        base="${file%.nc}"
        tmpfile="${base}_tmp.nc"
        if $USE_NCCOPY; then
            mv  "$file" "$tmpfile"; nccopy -d5 -s "$tmpfile" "$file"; rm "$tmpfile"
        else
            mv  "$file" "$tmpfile"; cdo -f "$FORMAT" -z "$COMPRESSION" copy "$tmpfile" "$file"; rm "$tmpfile"
        fi
        if [ $? -eq 0 ]; then
            echo "Compressed (in-place): $file"
        else
            echo "Error compressing: $file" >&2
            rm -f "$tmpfile"
        fi
    else
        # Create new file with suffix _compressed before extension
        base="${file%.nc}"
        newfile="${base}_cmp.nc"
        if [ -f "$newfile" ]; then
            echo "Skipping $file (target $newfile already exists)"
            continue
        fi
        if $USE_NCCOPY; then
            nccopy -d5 -s "$file" "$newfile"
        else
            cdo -f "$FORMAT" -z "$COMPRESSION" copy "$file" "$newfile"
        fi
        if [ $? -eq 0 ]; then
            echo "Compressed: $file -> $newfile"
        else
            echo "Error compressing: $file" >&2
            rm -f "$newfile"
        fi
    fi
done

echo "Done."
