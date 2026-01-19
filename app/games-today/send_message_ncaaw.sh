#! /usr/bin/bash

date >> /home/kurt/cronlogs/ncaaw.log

cd /home/kurt/git/game-day
source .venv/bin/activate
python send_message.py
deactivate
