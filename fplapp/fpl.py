import json
import requests



def get_league_teams(leagueID):

    newdict = {}

    url = "https://fantasy.premierleague.com/api/leagues-classic/" + str(leagueID) + "/standings/"
    req = requests.get(url)
    l=req.json()
    for i in l['standings']['results']:
        newdict[i['entry_name']] = {str(i['id'])}

    return newdict

def get_user_leagues_info(userID):
    newdict = {}

    url = "https://fantasy.premierleague.com/api/entry/" + str(userID) + "/"
    req = requests.get(url)
    if req.status_code != 404:
        l=req.json()
        for i in l['leagues']['classic']:
            newdict[i['name']] = i['entry_rank']

        return newdict
    else:
        return False

