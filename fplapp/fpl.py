import json
import pandas as pd
import requests
import pprint


regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
req = requests.get(regUrl)
if req.status_code != 404:
    league = json.loads(req.text)


# TODO Remove the temp dict and just append a dict straight to the list
def get_league_users(league_id):
    url = "https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/".format(league_id=league_id)
    req = requests.get(url)
    if req.status_code != 404:
        league = json.loads(req.text)

    league_players = []
    for person in league['standings']['results']:
        temp = {}
        temp['name'] = person['player_name']
        temp['team_id'] = person['entry']
        temp['team_name'] = person['entry_name']
        league_players.append(temp)
    return league_players






def get_user_player_list(user_id):
    url = "https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw}/picks/".format(user_id=user_id, gw =1)
    req = requests.get(url)
    if req.status_code != 404:
        players = json.loads(req.text)
    
    return [i['element']for i in players['picks']]

def get_user_history(user_id):
    url = "https://fantasy.premierleague.com/api/entry/{user_id}/history/".format(user_id=user_id)
    req = requests.get(url)
    if req.status_code != 404:
        history = json.loads(req.text)

    temp = []
    for i in history['current']:
        temp.append(
            {'gw': i['event'], 'gw_points': i['points'], 'total_points': i['total_points'], 'rank':i['rank'], 'rank_sort': i['rank_sort'], 
            'overall_rank': i['overall_rank'], 'bank': float(i['bank'])/10, 'team_value': float(i['value'])/10, 'gw_transfers': i['event_transfers'], 
            'gw_transfer_cost': i['event_transfers_cost'], 'gw_bench_points': i['points_on_bench']
            }
        )
    return temp

def get_user_player_info(user_player_list):
    temp = []
    for i in league['elements']:
        if i['id'] in user_player_list:
            temp.append(i)
    return temp





def create_fpl_list(league_id):
    lp = get_league_users(league_id)
    for i in lp:
    # i['player_list'] = get_user_player_info(get_user_player_list(i['team_id']))
        i['player_history'] = get_user_history(i['team_id'])
        
    data = []
    for j in lp:
        t = {'name': j['team_name'], 'gw': [0], 'gw_points':[0],'total_points': [0], 'gw_bench_points': [0], 'total_bench_points': [0], 
                'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 'total_transfers': [0],'team_value': [100.0]}
        for i in j['player_history']:
            t['gw'].append(int(i['gw']))
            t['gw_points'].append(int(i['gw_points']))
            t['total_points'].append(int(i['total_points']))
            t['gw_bench_points'].append(int(i['gw_bench_points']))
            t['total_bench_points'].append(sum(t['total_bench_points']) + i['gw_bench_points'])
            t['gw_transfer_cost'].append(i['gw_transfer_cost'])
            t['total_transfer_cost'].append(sum(t['total_transfer_cost']) + i['gw_transfer_cost']) 
            t['gw_transfers'].append(int(i['gw_transfers']))
            t['total_transfers'].append(sum(t['gw_transfers']) + i['gw_transfers'])
            t['team_value'].append(float(i['team_value']))
            
        data.append(t)
    return data


def get_player_data(user_id):
    regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    req = requests.get(regUrl)
    if req.status_code != 404:
        league = json.loads(req.text  )

    for i in league['elements']:
        if i['id'] == 14:
            print(i)

# df['game_week'] = 1
# df.to_csv('fpl_data_2021.csv')
# print(df)