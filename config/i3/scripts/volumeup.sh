#!/bin/sh

#amixer set Master 5+
#a=`amixer get Master |grep % |awk '{print $5}'|sed -e 's/\[//' -e 's/\]//'`
#dunstify "Volume up(${a:0:3})"

VOLUME='+1%'
for SINK in `pacmd list-sinks | grep 'index:' | cut -b12-`
do
  pactl set-sink-volume $SINK $VOLUME
done
