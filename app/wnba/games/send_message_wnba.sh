#! /usr/bin/bash

# clean log file
rm -f send_message_wnba_games.log

date >> /home/kurt/cronlogs/wnba.log
date > send_message_wnba_games.log

cd /home/kurt/git/game-day/app/wnba/standings || exit
source .venv/bin/activate
python send_message.py --live >> send_message_wnba_games.log 2>&1
deactivate
