#! /usr/bin/bash

# clean log file
rm -f send_message_nwsl_games.log

date >> /home/kurt/cronlogs/nwsl.log
date > send_message_nwsl_games.log

cd /home/kurt/git/game-day/app/nwsl/games || exit
source .venv/bin/activate
python send_message.py --live >> send_message_nwsl_games.log 2>&1
deactivate
