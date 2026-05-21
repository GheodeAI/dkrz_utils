#!/bin/bash
# Recursively compress NetCDF files under a given path to NetCDF4 zip.
# Usage: ./compress_nc_recursive.sh /path/to/search [--replace] [--nccopy] [--level N]

set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 <directory> [--replace] [--nccopy] [--level N]

  <directory> : root directory to search for .nc files
  --replace   : replace original files (otherwise creates *_cmp.nc)
  --nccopy    : use nccopy if available (default: use cdo)
  --level N   : compression level 1..9 for zip (default: 5)

Example:
  $0 ./data --level 7
  $0 ./data --replace --nccopy --level 9
EOF
    exit 1
}

# ---------- compression functions ----------
compress_inplace() {
    local file="$1"
    local tmpfile="${file%.nc}_tmp.nc"
    mv "$file" "$tmpfile"
    if $USE_NCCOPY; then
        nccopy -d"$COMPRESSION_LEVEL" -s "$tmpfile" "$file"
    else
        cdo -f nc4 -z "zip_$COMPRESSION_LEVEL" copy "$tmpfile" "$file"
    fi
    rm "$tmpfile"
}

compress_new() {
    local file="$1"
    local newfile="$2"
    if $USE_NCCOPY; then
        nccopy -d"$COMPRESSION_LEVEL" -s "$file" "$newfile"
    else
        cdo -f nc4 -z "zip_$COMPRESSION_LEVEL" copy "$file" "$newfile"
    fi
}

# ---------- parse arguments ----------
SEARCH_DIR=""
REPLACE=false
USE_NCCOPY=false          # default: use cdo
COMPRESSION_LEVEL=5

while [[ $# -gt 0 ]]; do
    case "$1" in
        --replace)
            REPLACE=true
            shift
            ;;
        --nccopy)
            USE_NCCOPY=true
            shift
            ;;
        --level)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --level requires a number (1-9)"
                usage
            fi
            if [[ ! "$2" =~ ^[1-9]$ ]]; then
                echo "Error: compression level must be between 1 and 9"
                usage
            fi
            COMPRESSION_LEVEL="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        -*)
            echo "Error: unknown option $1"
            usage
            ;;
        *)
            if [[ -z "$SEARCH_DIR" ]]; then
                SEARCH_DIR="$1"
                shift
            else
                echo "Error: multiple directory arguments provided"
                usage
            fi
            ;;
    esac
done

# check mandatory directory
if [[ -z "$SEARCH_DIR" ]]; then
    echo "Error: missing directory argument"
    usage
fi

if [[ ! -d "$SEARCH_DIR" ]]; then
    echo "Error: Directory '$SEARCH_DIR' does not exist."
    exit 1
fi

# ---------- decide which tool to use ----------
if $USE_NCCOPY; then
    if command -v nccopy &>/dev/null; then
        echo "Using nccopy for compression (level $COMPRESSION_LEVEL)."
    else
        echo "Warning: nccopy not found, falling back to cdo (level $COMPRESSION_LEVEL)."
        USE_NCCOPY=false
    fi
else
    echo "Using cdo for compression (level $COMPRESSION_LEVEL)."
fi

# ---------- process files ----------
find "$SEARCH_DIR" -type f -name "*.nc" -print0 | while IFS= read -r -d '' file; do
    if $REPLACE; then
        if compress_inplace "$file"; then
            echo "Compressed (in-place): $file"
        else
            echo "Error compressing: $file" >&2
        fi
    else
        base="${file%.nc}"
        newfile="${base}_cmp.nc"
        if [[ -f "$newfile" ]]; then
            echo "Skipping $file (target $newfile already exists)"
            continue
        fi
        if compress_new "$file" "$newfile"; then
            echo "Compressed: $file -> $newfile"
        else
            echo "Error compressing: $file" >&2
            rm -f "$newfile"
        fi
    fi
done

echo "Done."
