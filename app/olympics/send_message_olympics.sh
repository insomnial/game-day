#! /usr/bin/bash

date >> /home/kurt/cronlogs/olympics.log

cd /home/kurt/git/game-day/app/olympics
source ../../.venv/bin/activate
python send_message.py
deactivate
