#! /usr/bin/bash

# clean log file
rm -f send_message_mlb_games.log

date >> /home/kurt/cronlogs/mlb.log
date > send_message_mlb_games.log

cd /home/kurt/git/game-day/app/mlb/games || exit
source .venv/bin/activate
python send_message.py --live >> send_message_mlb_games.log 2>&1
deactivate
