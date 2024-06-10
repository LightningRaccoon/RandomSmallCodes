#!/bin/bash

# Check if there are at least 9 arguments
if [ -z "$9" ]; then
    echo "No 9th argument"
    exit 1
fi

# Get the directory of the script file
targetPath="$(dirname "$(readlink -f "$0")")"

# Remove trailing slash if it exists
targetPath="${targetPath%/}"

# Get the parent directory
parentPath="$(dirname "$targetPath")"

# Remove trailing slash if it exists
parentPath="${parentPath%/}"

# Set the output file
outputStatistics="statistics.txt"

{
    echo "Number of drivers in the championship:   $1"
    echo "Number of engine manufacturers:          $2"
    echo "Number of images:                        $3"
    echo "Number of identified images:             $4"
    echo "Number of unidentified images:           $5"
    echo "Size of all images:                      $6"
    echo "Average size of images:                  $7"
    echo "Highest resolution image:                $8"
    echo "Lowest resolution image:                 $9"
} > "$parentPath/$outputStatistics"

echo "Statistics saved to $parentPath/$outputStatistics"
