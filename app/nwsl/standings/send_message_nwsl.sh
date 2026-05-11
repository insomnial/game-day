#! /usr/bin/bash

# clean log file
rm -f send_message_nwsl.log

date >> /home/kurt/cronlogs/nwsl.log
date > send_message_nwsl.log

cd /home/kurt/git/game-day/app/nwsl/standings || exit
source .venv/bin/activate
python send_message.py --live >> send_message_nwsl.log 2>&1
deactivate
