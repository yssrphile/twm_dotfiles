#!/usr/bin/env bash

PICTURE=/tmp/i3lock.png
SCREENSHOT="gnome-screenshot -f $PICTURE"

#BLUR="5x4"
BLUR="0x20"

$SCREENSHOT
convert $PICTURE -blur $BLUR $PICTURE
i3lock -i $PICTURE
rm $PICTURE
