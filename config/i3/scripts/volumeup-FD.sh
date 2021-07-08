#!/bin/sh

#amixer set Master 1+
#a=`amixer get Master |grep % |awk '{print $5}'|sed -e 's/\[//' -e 's/\]//'`
#dunstify "Volume up(${a:0:3})"


#VOLUME='+1%'
#for SINK in `pacmd list-sinks | grep 'index:' | cut -b12-`
#do
#  pactl set-sink-volume $SINK $VOLUME
#done


#pactl set-sink-volume @DEFAULT_SINK@ +1%



##### PREVENT MAX VOLUME FROM EXCEEDING 100% #####
x=$(pactl list sinks | grep '^[[:space:]]Volume:' | head -n $(( $SINK + 1 )) | tail -n 1 | sed -e 's,.* \([0-9][0-9]*\)%.*,\1,' )
if [[ $x -le 99 ]]
then
    pactl set-sink-volume @DEFAULT_SINK@ +1%
fi
