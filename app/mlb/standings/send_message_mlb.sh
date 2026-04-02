#! /usr/bin/bash

date >> /home/kurt/cronlogs/mlb.log

cd /home/kurt/git/game-day/app/mlb/standings || exit
source ../../../.venv/bin/activate
python send_message.py
deactivate
