# import json
# import pandas as pd
# import requests
# import pprint
# import time

# def request_error_check(url):
#     try:
#         req = requests.get(url)
#         req.raise_for_status()
#     except requests.exceptions.HTTPError as errh:
#         return (f"Http Error: {errh}")
#     except requests.exceptions.ConnectionError as errc:
#         return (f"Error Connecting: {errc}")
#     except requests.exceptions.Timeout as errt:
#         return (f"Timeout Error: {errt}")
#     except requests.exceptions.RequestException as err:
#         return (f"Uh Oh: Something Else {err}")
    
#     return json.loads(req.text)

# def get_base_url():
#     regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
#     req = requests.get(regUrl)
#     if req.status_code != 404:
#         league = json.loads(req.text)
#     return league


# def get_league_users(league_id):
#     url = "https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/".format(league_id=league_id)
    
    
#     league = request_error_check(url)
#     if type(league) is str:
#         return league
#     else:
#         league_players = []
#         for person in league['standings']['results']:
#             league_players.append({'name': person['player_name'], 'team_id': person['entry'], 'team_name': person['entry_name'], 'rank': person['rank'], 'last_rank': person['last_rank']})
#         return league_players


# def get_user_player_list(user_id):
#     url = "https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw}/picks/".format(user_id=user_id, gw =1)
#     req = requests.get(url)
#     if req.status_code != 404:
#         players = json.loads(req.text)
    
#     return [i['element']for i in players['picks']]

# def get_user_history(user_id):
#     url = "https://fantasy.premierleague.com/api/entry/{user_id}/history/".format(user_id=user_id)
#     req = requests.get(url)
#     if req.status_code != 404:
#         history = json.loads(req.text)

#     temp = {'gw': [0], 'gw_points':[0],'total_points': [0], 'gw_rank':[0], 'rank_sort':[0], 'overall_rank':[0],'gw_bench_points': [0], 
#         'total_bench_points': [0], 'bank': [0], 'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 
#         'total_transfers': [0],'team_value': [100.0], 'chips': [], 'past_seasons': [], 'total_value': [100.0], 'gw_value_diff':[0]}
#     for i in history['current']:
#         temp['gw'].append(int(i['event']))
#         temp['gw_points'].append(int(i['points']))
#         temp['total_points'].append(int(i['total_points']))
#         temp['gw_rank'].append(int(i['rank']))
#         temp['rank_sort'].append(int(i['rank_sort']))
#         temp['overall_rank'].append(int(i['overall_rank']))
#         temp['bank'].append(float(i['bank'])/10)
#         temp['gw_bench_points'].append(int(i['points_on_bench']))
#         temp['total_bench_points'].append(temp['total_bench_points'][-1] + i['points_on_bench'])
#         temp['gw_transfer_cost'].append(i['event_transfers_cost'])
#         temp['total_transfer_cost'].append(temp['total_transfer_cost'][-1] + i['event_transfers_cost']) 
#         temp['gw_transfers'].append(int(i['event_transfers']))
#         temp['total_transfers'].append(temp['total_transfers'][-1] + i['event_transfers'])
#         temp['total_value'].append(float(i['value'])/10)
#         temp['team_value'].append(float("{0:.2f}".format(temp['total_value'][-1] - temp['bank'][-1])))
#     for i in history['past']:
#         temp['past_seasons'].append({'year': i['season_name'], 'past_total_points': i['total_points'], 'finishing_rank': i['rank']})
#     for i in history['chips']:
#         chip_names = {'wildcard': 'Wildcard', '3xc': "Triple Captain"}
#         temp['chips'].append({'name': chip_names[i['name']], 'gw_used': i['event']})
#     for i in range(len(temp['total_value'])):
#         if i > 0:
#             temp['gw_value_diff'].append(temp['total_value'][i] - temp['total_value'][i-1])
#     return temp

# def create_fpl_list(league_id):
#     chip_dict = {'Wildcard': 0, 'Triple Captain': 0}
#     firsttime = time.time()
#     league_members = get_league_users(league_id)
#     endfirst = time.time()
#     print(f"First: {endfirst - firsttime}")
#     if type(league_members) is str:
#         return league_members
#     else:
#         sectime = time.time()
#         for member in league_members:
#             member.update(get_user_history(member['team_id']))
#             if member['chips']:
#                 for i in member['chips']:
#                     chip_dict[i['name']] += 1
#         endsec = time.time()
#         print(f"Sec: {endsec-sectime}")
#         return (league_members, chip_dict)

