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
    echo "  clint           Change to /work/bk1318/b382610/ (default)"
    echo "  medewsa         Change to /work/bb1478/b382610/"
    echo "  carmine         Change to /work/bb1481/b382610/"
    echo "  nuria           Change to /work/bk1318/b383264/"
    echo
    echo "If no argument is provided, 'clint' is used as the default."
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
    arg1=${1:-"clint"}

    # Change directory based on the argument
    if [ "$arg1" == "clint" ]; then
        cd /work/{PROJ1}/{USER}/
    elif [ "$arg1" == "medewsa" ]; then
        cd /work/{PROJ2}/{USER}/
    elif [ "$arg1" == "carmine" ]; then
        cd /work/{PROJ3}/{USER}/
    elif [ "$arg1" == "nuria" ]; then
        cd /work/{PROJ4}/{USER}/
    else
        echo "Invalid argument: $arg1"
        echo "Usage: cd_work [clint|medewsa|carmine|nuria]"
    fi
fi
