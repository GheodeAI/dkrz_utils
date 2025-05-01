#!/bin/bash

# Function to display help message
show_help() {
    echo "Usage: $0 [OPTION] PORT [PATH_ARG]"
    echo "Initialize Jupyter-Lab on the specified port and change directory."
    echo
    echo "Options:"
    echo "  -h, --help      Show this help message and exit"
    echo
    echo "Arguments:"
    echo "  PORT            Port number to run Jupyter-Lab (mandatory)"
    echo "  PATH_ARG        Directory to change to (${NAMEPROJ1}, ${NAMEPROJ2}, ${NAMEPROJ3}, here) (default: ${NAMEPROJ1})"
}

# Check for help option in any argument
for arg in "$@"; do
    if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
        show_help
        exit 0
    fi
done

# Check if port is provided
if [ -z "$1" ]; then
    echo "Error: No port provided."
    show_help
else
    PORT=$1
    # Set PATH_ARG to the second argument if provided, otherwise default to ${NAMEPROJ1}
    if [ -n "$2" ]; then
        PATH_ARG="$2"
    else
        PATH_ARG=${1:-"${NAMEPROJ1}"}
    fi

    # Determine directory based on PATH_ARG
    if [[ "$PATH_ARG" == "${NAMEPROJ1}" ]]; then
        CD_PATH="/work/${PATHPROJ1}/${USER}/"
    elif [[ "$PATH_ARG" == "${NAMEPROJ2}" ]]; then
        CD_PATH="/work/${PATHPROJ2}/${USER}/"
    elif [[ "$PATH_ARG" == "${NAMEPROJ3}" ]]; then
        CD_PATH="/work/${PATHPROJ3}/${USER}/"
    elif [[ "$PATH_ARG" == "here" ]]; then
        CD_PATH="."
    else
        echo "Invalid PATH_ARG: $PATH_ARG. Valid options are clint, medewsa, carmine."
    fi

    # If CD_PATH is set (i.e., PATH_ARG is valid), proceed with the rest of the script
    if [ -n "$CD_PATH" ]; then
        echo "Loading modules..."
        module load cdo
        module load nano
        module load pytorch

        echo "Activating conda..."
        source activate
        conda activate
        conda activate ${ENV1}

        echo "Changing path to $CD_PATH..."
        cd "$CD_PATH" || { echo "Failed to change directory to $CD_PATH"; }

        echo "And there it goes the Jupyter..."
        jupyter-lab --no-browser --port=$PORT
    fi
fi
