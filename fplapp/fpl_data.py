import json
import pandas as pd
import requests
from pprint import pprint
from collections import Counter

class FplData():
    
    def __init__(self):
        self.league_data = None
        self.chip_names = {"wildcard": "Wildcard1", "3xc": "Triple-Captain", 'bboost': "Bench-boost"}
        self.chip_count_dict = {'Wildcard1': 0, 'Triple-Captain': 0, 'Bench-boost': 0, 'Free-hit': 0}
        self.chips_used = []
        self.member_chip_list = []
        self.member_highest_gw_score = {}
        self.gw_points = {}
        self.max_points_per_gw = []
        self.min_points_per_gw = []

    
    def request_error_check(self, url):
        """
        Checks request response for errors or if FPL API is updating. 
        
        Parameters:
            url (str): Url to request
        Returns:
            json or tuple: If there is an error or update message will return a tuple with type and string. Otherwise, returns json object
        """
        
        try:
            req = requests.get(url)
            req.raise_for_status()
            if type(req) is str and req == "The game is being updated.":
                return ("Updating", "FPL is currently being updated.")
        
            return req.json()
        except requests.exceptions.HTTPError as errh:
            return ("Error", f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            return ("Error", f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            return ("Error", f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            return ("Error", f"Uh Oh: Something Else {err}")
    
    def set_league_user_data(self, league_json_response):
        """
        Appends member info dict to league_data list
        
        Parameters: 
            league_json_response (JSON): JSON object containing FPL league standings
        """
        self.league_data = [{ 'name': person.get('player_name'), 'team_id': person.get('entry'), 
                            'team_name': person.get('entry_name'), 'rank': person.get('rank'), 'last_rank': person.get('last_rank')} 
                            for person in league_json_response['standings']['results']]

    #TODO this is sort of ugly
    def set_user_history(self, team_name, history_json_response):
        """
        Parses history json to dict
        
        Parameters:
            team_name (str): String of league members name
        
        Returns:
            dict: Dictionary of parsed JSON
        """

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
    
    # TODO pick one
    def set_member_chip_list(self, chip_list, team_name):
        self.member_chip_list.append({'team_name': team_name, 'chips': [i['chip_name'] for i in chip_list]})
    
    # TODO pick one
    def set_chips_used(self, chip_list, team_name):
        for i in chip_list:
            self.chips_used.append({'team_name': team_name,'chip_name': i['chip_name'], 'gw_used': i['gw_used']})

    def count_chips(self, chip_list):
        for i in chip_list:
            self.chip_count_dict[i['chip_name']] += 1
    
    # TODO pick one         
    def set_player_chips(self, chip_json):
        return [{'chip_name': self.chip_names[i['name']], 'gw_used': i['event']} for i in chip_json]

    # TODO Docstring
    def set_past_seasons(self, past_json):
        return [{'year': i['season_name'], 'past_total_points': i['total_points'], 'finishing_rank': i['rank']} for i in past_json]


    def calc_gw_team_value_diff(self, total_value_list):
        """
        Calculates total team value difference between gameweeks
        
        Parameters:
            total_value_list (list): List of total team value per gameweeks
        Returns:
            list: List containing total value difference between gameweeks
        """
        return [total_value_list[i] - total_value_list[i-1] if i > 0 else 0 for i in range(len(total_value_list))]
    
    
    def create_fpl_list(self, league_id):
        """Sort of a driver for setting all class variables"""
        league_json_response = self.request_error_check(f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/")
        if type(league_json_response) is tuple:
            return league_json_response
        
        self.set_league_user_data(league_json_response)
        
        for member in self.league_data:
            history_json_response = self.request_error_check(f"https://fantasy.premierleague.com/api/entry/{member['team_id']}/history/")
            if type(history_json_response) is tuple:
                return history_json_response
            
            member.update(self.set_user_history(member['team_name'], history_json_response))
            member['max_gw_points'] = max(member['gw_points'])
            member['max_gw_points_gw'] = member['gw_points'].index(member['max_gw_points'])
            self.set_gw_points(member)
        
        self.find_max_points_per_gw()
        self.find_min_points_per_gw()
        


    def get_most_points_scored_in_a_gw(self):
        """
        Finds the member who scored the most points in a single gw
        
        Returns:
            list: List of dicts (if mulitple people have same max)
        """
        max_points = max(self.max_points_per_gw, key=lambda x:x['points'])['points']
        return [member for member in self.max_points_per_gw if member['points'] == max_points]
        

    # TODO Docstring refactor
    def set_gw_points(self, member):
        for i in range(1, len(member['gw_points'])):
            if i in self.gw_points:
                self.gw_points[i].append({'team_name': member['team_name'], 'points': member['gw_points'][i]})
            else:
                self.gw_points[i] = [{'team_name': member['team_name'], 'points': member['gw_points'][i]}]

    # TODO Docstring refactor
    def find_max_points_per_gw(self):
        """Search list of lists of dicts. Ex: gw[0] = [{}{}{}{}]"""
        for k, v in self.gw_points.items():
            max_points = max(v, key=lambda x:x['points'])['points'] # max will return the dict so the added points only returns the points
            for i in v:
                if i['points'] == max_points:
                    self.max_points_per_gw.append({'gw': k, 'team_name': i['team_name'], 'points': i['points']})

    # TODO Docstring refactor
    def find_min_points_per_gw(self):
        for k, v in self.gw_points.items():
            min_points = min(v, key=lambda x:x['points'])['points']
            for i in v:
                if i['points'] == min_points:
                    self.min_points_per_gw.append({'gw': k, 'team_name': i['team_name'], 'points': i['points']})


    def count_gw_leader(self):
        """
        Counts number times player had most gameweek points
        
        Returns:
            dict: Sorted dict with team_name and leader count
        """
        temp = {i['team_name']: 0 for i in self.league_data}
        for i in self.max_points_per_gw:
            temp[i['team_name']] += 1
        
        return sorted(temp.items(), key=lambda x: x[1], reverse=True)


    def count_gw_lowest(self):
        """
        Counts number times player had least gameweek points
        
        Returns:
            dict: Sorted dict with team_name and min count
        """
        temp = {i['team_name']: 0 for i in self.league_data}
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


    def check_total_points_updated(self, current_points):
        """
        Updates total score if game is live
        
        Parameters:
            current_points (dict): Dict of teams and current points from FPL_Players class
        Returns:
            list: Sorted and updated league_data list of dicts
        """
        # NOTE: Because of the way the FPL API league endpoint is set up. It will only update total points after all the games for the day are completed.
        # However, the FPL API player endpoint will have live points. 
        if self.league_data[0]['total_points'][-1] != (self.league_data[0]['total_points'][-2] + current_points[self.league_data[0]['team_id']]):
            for i in self.league_data:
                i['total_points'][-1] = i['total_points'][-2] + current_points[i['team_id']]
        return sorted(self.league_data, key=lambda k: k['total_points'][-1], reverse=True)

