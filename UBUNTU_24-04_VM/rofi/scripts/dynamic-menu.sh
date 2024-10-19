#!/bin/bash

# List the last 10 modified files from your home directory
find ~ -type f -printf "%T@ %p\n" | sort -n | tail -10 | awk '{$1=""; print $0}' | rofi -dmenu -i -p "Select a file"
