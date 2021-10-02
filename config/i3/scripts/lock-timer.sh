#!/usr/bin/env bash

exec xautolock -restart \
  -detectsleep \
  -time 1 -locker "~/.config/i3/scripts/blur-lock2.sh" \
  -notify 10 \
  -notifier "notify-send -u critical -t 9000 -- 'LOCKING screen in 10 seconds'"

