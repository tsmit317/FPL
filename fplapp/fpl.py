import json
import requests

url = "https://fantasy.premierleague.com/api/leagues-classic/889946/standings/"
url_team = "https://fantasy.premierleague.com/api/entry/3557697/"
r = requests.get(url_team)


j = r.json()

url = 'https://fantasy.premierleague.com/api/leagues-classic/'



def get_league_teams(leagueID):

    newdict = {}

    url = "https://fantasy.premierleague.com/api/leagues-classic/" + str(leagueID) + "/standings/"
    req = requests.get(url)
    l=req.json()
    for i in l['standings']['results']:
        newdict[i['entry_name']] = {str(i['id'])}

    return newdict

def determine_rank(userID):
    
