import json
import pandas as pd
import requests
import pprint


class FplData():
    
    def __init__(self):
        self.league_data = []
        self.chip_dict = {'Wildcard': 0, 'Triple Captain': 0, 'Bench boost': 0, 'Free hit': 0}
        self.member_highest_gw_score = {}
        
        
    def request_error_check(self, url):
        try:
            req = requests.get(url)
            req.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return (f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            return (f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            return (f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            return (f"Uh Oh: Something Else {err}")
        
        return req.json()
        
        
    def get_league_users(self, league_id):
        url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
        
        league_json_response = self.request_error_check(url)
        if type(league_json_response) is str:
            self.league_data = league_json_response
        else:
            for person in league_json_response['standings']['results']:
                self.league_data.append({'name': person['player_name'], 'team_id': person['entry'], 'team_name': person['entry_name'], 'rank': person['rank'], 'last_rank': person['last_rank']})
    
    
    def get_user_history(self, user_id):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"
        
        history_json_response = self.request_error_check(url)
        if type(history_json_response) is str:
            self.league_data = history_json_response
        

        temp = {'gw': [0], 'gw_points':[0],'total_points': [0], 'gw_rank':[0], 'rank_sort':[0], 'overall_rank':[0],'gw_bench_points': [0], 
            'total_bench_points': [0], 'bank': [0], 'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 
            'total_transfers': [0],'team_value': [100.0], 'chips': [], 'past_seasons': [], 'total_value': [100.0], 'gw_value_diff':[0]}
        
        for i in history_json_response['current']:
            temp['gw'].append(int(i['event']))
            temp['gw_points'].append(int(i['points']))
            temp['total_points'].append(int(i['total_points']))
            temp['gw_rank'].append(int(i['rank']))
            temp['rank_sort'].append(int(i['rank_sort']))
            temp['overall_rank'].append(int(i['overall_rank']))
            temp['bank'].append(float(i['bank'])/10)
            temp['gw_bench_points'].append(int(i['points_on_bench']))
            temp['total_bench_points'].append(temp['total_bench_points'][-1] + i['points_on_bench'])
            temp['gw_transfer_cost'].append(i['event_transfers_cost'])
            temp['total_transfer_cost'].append(temp['total_transfer_cost'][-1] + i['event_transfers_cost']) 
            temp['gw_transfers'].append(int(i['event_transfers']))
            temp['total_transfers'].append(temp['total_transfers'][-1] + i['event_transfers'])
            temp['total_value'].append(float(i['value'])/10)
            temp['team_value'].append(float("{0:.2f}".format(temp['total_value'][-1] - temp['bank'][-1])))
        for i in history_json_response['past']:
            temp['past_seasons'].append({'year': i['season_name'], 'past_total_points': i['total_points'], 'finishing_rank': i['rank']})
        for i in history_json_response['chips']:
            chip_names = {'wildcard': 'Wildcard', '3xc': "Triple Captain"}
            temp['chips'].append({'name': chip_names[i['name']], 'gw_used': i['event']})
            self.chip_dict[chip_names[i['name']]] += 1
        for i in range(len(temp['total_value'])):
            if i > 0:
                temp['gw_value_diff'].append(temp['total_value'][i] - temp['total_value'][i-1])
        return temp

    def create_fpl_list(self, league_id):
        self.get_league_users(league_id)
        if type(self.league_data[0]) is dict:
            for member in self.league_data:
                member.update(self.get_user_history(member['team_id']))
                member['max_gw_points'] = max(member['gw_points'])
                member['max_gw_points_gw'] = member['gw_points'].index(member['max_gw_points'])
    
    def get_league_data(self):
        return self.league_data

    def get_league_chips(self):
        return self.chip_dict
    
    # def set_member_max_point_gw(self):
    #     for member in self.league_data:
    #         member['max_gw_points'] = max(member['gw_points'])
    #         member['max_gw_points_gw'] = member['gw_points'].index(member['max_gw_points'])
    
    def get_most_points_scored_in_a_gw(self):
        highest_gw_score = {'team_name': '', 'points': 0, 'gw': 0}
        for member in self.league_data:
            if max(member['gw_points']) > highest_gw_score['points']:
                highest_gw_score['team_name'] = member['team_name']
                highest_gw_score['points'] = max(member['gw_points'])
                highest_gw_score['gw'] = member['gw_points'].index(highest_gw_score['points'])
        return highest_gw_score
    
  