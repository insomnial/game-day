import os, statsapi, json
from dotenv import load_dotenv
from pathlib import Path

from requests import get
from datetime import datetime


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
GAME_DIR = 'stack_game/'


###############################################################################
#region Private functions
###############################################################################


###############################################################################
#region Public functions
###############################################################################


# Main for testing, functions will be called by send_message.py
def main():

    print(statsapi.linescore(825007)) # (game_id)
    print(statsapi.game_highlights(825007)) # (game_id)
    highlight_json = statsapi.game_highlight_data(statsapi.last_game(137))
    # print(json.dumps(highlight_json, indent=4))


# I forget this every effing time
if __name__ == '__main__':
    main()
