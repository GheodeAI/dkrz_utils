#!/bin/bash

# Function to display help message
show_help() {
    echo "Usage: cd_work [OPTION] [ARGUMENT]"
    echo "Load modules and change to a specified directory."
    echo
    echo "Options:"
    echo "  -h, --help      Show this help message and exit"
    echo
    echo "Arguments:"
    echo "  ${NAMEPROJ1}           Change to /work/${PATHPROJ1}/${USER}/ (default)"
    echo "  ${NAMEPROJ2}         Change to /work/${PATHPROJ2}/${USER}/"
    echo "  ${NAMEPROJ3}         Change to /work/${PATHPROJ3}/${USER}/"
    echo "  ${NAMEPROJ4}           Change to /work/${PATHPROJ4}/"
    echo
    echo "If no argument is provided, '${NAMEPROJ1}' is used as the default."
}

# Check for help option
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
else
    # Load the required modules
    module load cdo
    module load nano
    module load ncview

    # Set the default argument to "clint" if no argument is provided
    arg1=${1:-"${NAMEPROJ1}"}

    # Change directory based on the argument
    if [ "$arg1" == "${NAMEPROJ1}" ]; then
        cd "/work/${PATHPROJ1}/${USER}/"
    elif [ "$arg1" == "${NAMEPROJ2}" ]; then
        cd "/work/${PATHPROJ2}/${USER}/"
    elif [ "$arg1" == "${NAMEPROJ3}" ]; then
        cd "/work/${PATHPROJ3}/${USER}/"
    elif [ "$arg1" == "${NAMEPROJ4}" ]; then
        cd "/work/${PATHPROJ4}/"
    else
        echo "Invalid argument: $arg1"
        show_help
    fi
fi
