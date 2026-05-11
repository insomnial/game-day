import os, statsapi
from dotenv import load_dotenv
from pathlib import Path


###############################################################################
#region Load variables
###############################################################################
# environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
# request
#NL West leagueId="104", division="203"
#NL East leagueId="104", division="204"

###############################################################################
#region Private functions
###############################################################################


###############################################################################
#region Public functions
###############################################################################
def get_division_standings(a_league, a_division) -> dict:
    league_string = f'{a_league}'
    division_string = f'{a_division}'
    response = statsapi.standings_data(
        leagueId=league_string,
        division=division_string,
        include_wildcard=True,
        season=None,
        standingsTypes=None, 
        date=None
    )
    return response

# Main for testing, functions will be called by send_message.py
def main():
    # print( statsapi.standings(leagueId="104", division="203", include_wildcard=True, season=None, standingsTypes=None, date=None) )
    # print( statsapi.standings_data(leagueId="104", division="203", include_wildcard=True, season=None, standingsTypes=None, date=None) )
    print( get_division_standings(104, 203) )

# I forget this every effing time
if __name__ == '__main__':
    main()
