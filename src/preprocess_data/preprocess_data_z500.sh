#!/bin/bash

# Default value for optional argument
reg_arg='.*/E5.*\.grb'
#'.*/E5.*(194[0-9]|19[5-9][0-9]|20[0-1][0-9]|202[0-2]).*129\.grb'

# Function to display help
show_help() {
    echo "Usage: $0 <path-to-folder> <output-dir> [-r <regex>]"
    echo ""
    echo "   You need an out.grid to run this code. That is, the"
"$arg2""${f:32:end}"    echo "   grid configuration you what as output."
    echo ""
    echo "Arguments:"
    echo "  path-to-folder    Path to the folder where the original data is"
    echo "  output-dir        Path to the folder where to save the generated data."
    echo "  -r <regex>        Optional argument to specify RegEx, in order to "
    echo "                       filter the data (default: '$reg_arg')"
    echo "  -h                Show this help message"
    exit 0
}

# Check if no arguments were provided
if [[ $# -eq 0 ]]; then
    echo "Error: No arguments provided. Use -h for help."
    exit 1
fi

# Initialize positional argument counter
positional_args=()

# Manually parse arguments to allow `-r` anywhere
while [[ $# -gt 0 ]]; do
    case "$1" in
        -r)
            if [[ -n "$2" && "$2" != -* ]]; then
                reg_arg="$2"
                shift 2  # Move past `-r` and its value
            else
                echo "Error: -r requires a value." >&2
                exit 1
            fi
            ;;
        -h)
            show_help
            ;;
        -*)
            echo "Error: Invalid option $1" >&2
            exit 1
            ;;
        *)
            positional_args+=("$1")  # Store positional arguments
            shift
            ;;
    esac
done

# Ensure exactly 2 required positional arguments
if [[ ${#positional_args[@]} -ne 2 ]]; then
    echo "Error: Missing required arguments. Use -h for help."
    exit 1
fi

# Assign required arguments
arg1=${positional_args[0]}
arg2=${positional_args[1]}

FILES=$(find "$arg1" -type f -regextype posix-extended -regex "$reg_arg")

for f in $FILES
do
  cdo -sellevel,50000 "$f" "$arg2${f:32}"
  cdo -P 8 remapcon,n512 -setgridtype,regular "$arg2${f:32}" "$arg2${f:32:-4}_gg.grb"
  rm "$arg2${f:32}"
  cdo remapbil,out.grid "$arg2${f:32:-4}_gg.grb" "$arg2${f:32:-4}_g0.25.grb"
  rm "$arg2${f:32:-4}_gg.grb"
  cdo -f nc copy "$arg2${f:32:-4}_g0.25.grb" "$arg2${f:32:-4}_g0.25.nc"
  rm "$arg2${f:32:-4}_g0.25.grb"
done

