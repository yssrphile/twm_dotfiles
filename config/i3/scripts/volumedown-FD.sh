#!/bin/sh

#amixer set Master 1-
#a=`amixer get Master |grep % |awk '{print $5}'|sed -e 's/\[//' -e 's/\]//'`
#dunstify "Volume down(${a:0:3})"


#VOLUME='-1%'
#for SINK in `pacmd list-sinks | grep 'index:' | cut -b12-`
#do
#  pactl set-sink-volume $SINK $VOLUME
#done


pactl set-sink-volume @DEFAULT_SINK@ -1%
