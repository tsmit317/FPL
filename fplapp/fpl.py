import json
import requests


def get_user_leagues_info(userID):
    newdict = {}

    url = "https://fantasy.premierleague.com/api/entry/" + str(userID) + "/"
    req = requests.get(url)
    if req.status_code != 404:
        league = req.json()
        
        for i in league['leagues']['classic']:
            newdict[i['name']] = i['entry_rank']

        return newdict
    else:
        return False

