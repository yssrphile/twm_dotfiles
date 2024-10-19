#!/bin/bash

# Get the current wallpaper using nitrogen
###WALLPAPER=$(nitrogen --save | grep -oP '(?<=^).*')
##WALLPAPER=$(grep -m 1 'file=' ~/.config/nitrogen/bg-saved.cfg | cut -d'=' -f2)
WALLPAPER=~/Public/Sandbox/wallpapers/0187.png

# Create a blurred version of the wallpaper
convert "$WALLPAPER" -blur 0x50 "/tmp/blurred_wallpaper.png"

# Get i3 colors (adjust these according to your theme)
COLOR_FG="#e8dfd6"  # Foreground color
COLOR_BG="#021b21"  # Background color (this will be the overlay)

# Lock the screen using i3lock
###i3lock -i "/tmp/blurred_wallpaper.png" -f --color="$COLOR_BG" --inside-color="$COLOR_BG" --ring-color="$COLOR_FG" --keyhl-color="$COLOR_FG" --bshl-color="$COLOR_FG" --separator-color="$COLOR_BG"
i3lock -i "/tmp/blurred_wallpaper.png" -f -c "$COLOR_BG"
##i3lock -i "/tmp/blurred_wallpaper.png" -f -b
##i3lock -i ~/Public/Sandbox/wallpapers/0040c.png -f -d -c "$COLOR_BG"

# Clean up
rm "/tmp/blurred_wallpaper.png"

