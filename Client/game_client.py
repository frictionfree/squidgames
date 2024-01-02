import requests
import argparse
import random
import json
from games.sumquest_client import SumQuest_v1_0_Client

AUTHENTICATION_URL = "http://{0}/gameserver/api/v1.0/authenticate?username={1}&password={2}"
GET_GAME_URL = "http://{0}/gameserver/api/v1.0/getgame?game_name={1}"
SUBMIT_GAME_URL = "http://{0}/gameserver/api/v1.0/submit"

def main():
    # Register available games
    available_games = dict()
    available_games[SumQuest_v1_0_Client.name()] = SumQuest_v1_0_Client.play_game

    # Initialize command line
    parser = argparse.ArgumentParser(
                    prog='SquidGameClient',
                    description='The squid game client, connect to a squid game server, pick up tasks and submit back solutions.',
                    epilog='Enjoy')
    
    parser.add_argument('-s', '--server', default="127.0.0.1:5000")
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-g', '--game', default="SumQuest v1.0")
    args = parser.parse_args()

    if (not (args.game in available_games.keys()) ) :
        print ("Unsupported game: {0}".format(args.game))
        return -1       

    # Authenticate and get an auth token
    res = requests.get(AUTHENTICATION_URL.format(args.server, args.username, args.password))
    if res.status_code != 200 :
        print ("Authentication error")
        return -1
     
     # Get game
    token = res.json().get("authentication").get("token")
    res =requests.get(GET_GAME_URL.format(args.server, args.game), headers={"Authorization":token})
    if res.status_code != 200 :
        print (res.text)
        return -1

    # Invoke the relevant game solver
    game_parameters = res.json().get("game_params")
    solution = available_games[args.game](game_parameters)
    solutionPack = json.dumps(solution)

    # Submit game solution
    res =requests.post(SUBMIT_GAME_URL.format(args.server), data=str(solutionPack), headers={"Content-Type" : "application/json", "Authorization":token})
    if res.status_code != 200 :
        print (res.text)
        return -1
    
    print (res.text)
    return 0


if __name__ == "__main__":
    main()