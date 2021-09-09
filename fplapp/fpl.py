import json
import pandas as pd
import requests
import pprint


regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
req = requests.get(regUrl)
if req.status_code != 404:
    league = json.loads(req.text)


def get_league_users(league_id):
    url = "https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/".format(league_id=league_id)
    req = requests.get(url)
    if req.status_code != 404:
        league = json.loads(req.text)

    league_players = []
    for person in league['standings']['results']:
        league_players.append({'name': person['player_name'], 'team_id': person['entry'], 'team_name': person['entry_name']})
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

    temp = {'gw': [0], 'gw_points':[0],'total_points': [0], 'rank':[0], 'rank_sort':[0], 'overall_rank':[0],'gw_bench_points': [0], 
        'total_bench_points': [0], 'bank': [100], 'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 
        'total_transfers': [0],'team_value': [100.0], 'chips': [], 'past_seasons': []}
    for i in history['current']:
        temp['gw'].append(int(i['event']))
        temp['gw_points'].append(int(i['points']))
        temp['total_points'].append(int(i['total_points']))
        temp['rank'].append(int(i['rank']))
        temp['rank_sort'].append(int(i['rank_sort']))
        temp['overall_rank'].append(int(i['overall_rank']))
        temp['bank'].append(float(i['bank'])/10)
        temp['gw_bench_points'].append(int(i['points_on_bench']))
        temp['total_bench_points'].append(sum(temp['total_bench_points']) + i['points_on_bench'])
        temp['gw_transfer_cost'].append(i['event_transfers_cost'])
        temp['total_transfer_cost'].append(sum(temp['total_transfer_cost']) + i['event_transfers_cost']) 
        temp['gw_transfers'].append(int(i['event_transfers']))
        temp['total_transfers'].append(sum(temp['gw_transfers']) + i['event_transfers'])
        temp['team_value'].append(float(i['value'])/10)
    for i in history['past']:
        temp['past_seasons'].append({'year': i['season_name'], 'past_total_points': i['total_points'], 'finishing_rank': i['rank']})
    for i in history['chips']:
        temp['chips'].append({'name': i['name'], 'gw_used': i['event']})
    return temp

def create_fpl_list(league_id):
    league_members = get_league_users(league_id)
    for member in league_members:
        member.update(get_user_history(member['team_id']))
    return league_members

def get_user_player_info(user_player_list):
    temp = []
    for i in league['elements']:
        if i['id'] in user_player_list:
            temp.append(i)
    return temp


def get_player_data(user_id):
    regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    req = requests.get(regUrl)
    if req.status_code != 404:
        league = json.loads(req.text  )

    for i in league['elements']:
        if i['id'] == 14:
            print(i)
