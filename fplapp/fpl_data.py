import json
import pandas as pd
import requests
from pprint import pprint


class FplData():
    
    def __init__(self):
        self.league_data = []
        self.league_member_ids = []
        self.chip_names = {"wildcard": "Wildcard1", "3xc": "Triple-Captain", 'bboost': "Bench-boost"}
        self.chip_count_dict = {'Wildcard1': 0, 'Triple-Captain': 0, 'Bench-boost': 0, 'Free-hit': 0}
        self.chips_used = []
        self.member_chip_list = []
        self.member_highest_gw_score = {}
        self.gw_points = {}
        self.max_points_per_gw = []
        self.min_points_per_gw = []

    # TODO Request does not account for fpl-api updating
    # When FPL weekly deadline occurs, json returns 'Updating' message for about an hour
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
    
    # TODO Create new method to check JSON response. Violates SRP
    def get_league_users(self, league_id):
        league_json_response = self.request_error_check(f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/")
        if type(league_json_response) is str:
            self.league_data = league_json_response
        else:
            for person in league_json_response['standings']['results']:
                self.league_member_ids.append(person.get('entry'))
                self.league_data.append({ 'name': person.get('player_name'), 'team_id': person.get('entry'), 
                                        'team_name': person.get('entry_name'), 'rank': person.get('rank'), 'last_rank': person.get('last_rank')})

    #TODO Create new method to check JSON response. Violates SRP and is SPAGHETTI
    def get_user_history(self, user_id, team_name):
        
        history_json_response = self.request_error_check(f"https://fantasy.premierleague.com/api/entry/{user_id}/history/")
        if type(history_json_response) is str:
            self.league_data = history_json_response

        temp = {'gw': [0], 'gw_points':[0],'total_points': [0], 'gw_rank':[0], 'rank_sort':[0], 'overall_rank':[0],'gw_bench_points': [0], 
            'total_bench_points': [0], 'bank': [0], 'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 
            'total_transfers': [0],'team_value': [100.0], 'total_value': [100.0]}
        
        for i in history_json_response['current']:
            temp['gw'].append(int(i['event']))
            temp['gw_points'].append(int(i['points'] - i['event_transfers_cost']))
            temp['total_points'].append(int(i['total_points']))
            if i['rank'] == None or i['rank'] == 'null':
                temp['gw_rank'].append(0)
            elif type(i['rank']) is int:
                temp['gw_rank'].append(int(i['rank']))
            if i['rank_sort'] == None or i['rank_sort'] == 'null':
                temp['rank_sort'].append(0)
            elif type(i['rank_sort']) is int:
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
        
        temp['past_seasons'] = self.set_past_seasons(history_json_response['past'])
        temp['chips'] = self.set_player_chips(history_json_response['chips'])
        self.count_chips(temp['chips'])
        self.set_chips_used(temp['chips'], team_name)
        self.set_member_chip_list(temp['chips'], team_name)        
        temp['gw_value_diff'] = self.calc_gw_team_value_diff(temp['total_value'])
        
        return temp

    def set_member_chip_list(self, chip_list, team_name):
        self.member_chip_list.append({'team_name': team_name, 'chips': [i['chip_name'] for i in chip_list]})

    def set_chips_used(self, chip_list, team_name):
        for i in chip_list:
            self.chips_used.append({'team_name': team_name,'chip_name': i['chip_name'], 'gw_used': i['gw_used']})

    def count_chips(self, chip_list):
        for i in chip_list:
            self.chip_count_dict[i['chip_name']] += 1
            
    def set_player_chips(self, chip_json):
        return [{'chip_name': self.chip_names[i['name']], 'gw_used': i['event']} for i in chip_json]

    def set_past_seasons(self, past_json):
        return [{'year': i['season_name'], 'past_total_points': i['total_points'], 'finishing_rank': i['rank']} for i in past_json]
    
    def calc_gw_team_value_diff(self, total_value_list):
        return [total_value_list[i] - total_value_list[i-1] if i > 0 else 0 for i in range(len(total_value_list))]
    
    # TODO Create new method to check JSON response. Violates SRP
    def create_fpl_list(self, league_id):
        self.get_league_users(league_id)
        if type(self.league_data[0]) is dict:
            for member in self.league_data:
                member.update(self.get_user_history(member['team_id'], member['team_name']))
                member['max_gw_points'] = max(member['gw_points'])
                member['max_gw_points_gw'] = member['gw_points'].index(member['max_gw_points'])
                self.set_gw_points(member)
            
            self.find_max_points_per_gw()
            self.find_min_points_per_gw()


    def get_most_points_scored_in_a_gw(self):
        highest_gw_score = [{'team_name': '', 'points': 0, 'gw': 0}]
        for member in self.league_data:
            max_points = max(member['gw_points'])
            if max_points > highest_gw_score[0]['points']:
                highest_gw_score.pop()
                highest_gw_score.append({'team_name': member['team_name'], 'points':  max_points, 'gw': member['gw_points'].index(max_points)})
        
        for member in self.league_data:
            max_points = max(member['gw_points'])
            if max_points == highest_gw_score[0]['points'] and not(member['team_name'] == highest_gw_score[0]['team_name']) and not(member['gw'] == highest_gw_score[0]['gw']):
                highest_gw_score.append({'team_name': member['team_name'], 'points': max_points, 'gw': member['gw_points'].index(max_points)})     
        return highest_gw_score

    def set_gw_points(self, member):
        for i in range(1, len(member['gw_points'])):
            if i in self.gw_points:
                self.gw_points[i].append({'team_name': member['team_name'], 'points': member['gw_points'][i]})
            else:
                self.gw_points[i] = [{'team_name': member['team_name'], 'points': member['gw_points'][i]}]

    def find_max_points_per_gw(self):
        for k, v in self.gw_points.items():
            max_points = max(v, key=lambda x:x['points'])['points']
            l = []
            for i in v:
                if i['points'] == max_points:
                    self.max_points_per_gw.append({'gw': k, 'team_name': i['team_name'], 'points': i['points']})

    def find_min_points_per_gw(self):
        for k, v in self.gw_points.items():
            min_points = min(v, key=lambda x:x['points'])['points']
            l = []
            for i in v:
                if i['points'] == min_points:
                    self.min_points_per_gw.append({'gw': k, 'team_name': i['team_name'], 'points': i['points']})

    def count_gw_leader(self):
        temp = {}
        for i in self.league_data:
            temp[i['team_name']] = 0
        for i in self.max_points_per_gw:
            temp[i['team_name']] += 1
        
        return sorted(temp.items(), key=lambda x: x[1], reverse=True)

    def count_gw_lowest(self):
        temp = {}
        for i in self.league_data:
            temp[i['team_name']] = 0
        for i in self.min_points_per_gw:
            temp[i['team_name']] += 1
        
        return sorted(temp.items(), key=lambda x: x[1], reverse=True)

    def get_min_points_per_gw(self):
        return self.min_points_per_gw

    def get_max_points_per_gw(self):
        return self.max_points_per_gw   
    
    def get_member_chip_list(self):
        return self.member_chip_list
    
    def get_league_data(self):
        return self.league_data

    def get_chip_count(self):
        return self.chip_count_dict

    def get_chips_used_list(self):
        return sorted(self.chips_used, key=lambda k: k['gw_used'])

