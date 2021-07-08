#!/bin/sh

#for SINK in `pacmd list-sinks | grep 'index:' | cut -b12-`
#do
##  pactl set-sink-volume $SINK $VOLUME
#  pactl set-sink-mute 0 toggle
#done


pactl set-sink-mute @DEFAULT_SINK@ toggle
