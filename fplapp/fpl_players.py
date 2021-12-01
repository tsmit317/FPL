import pandas as pd
import requests
import numpy as np

class FplPlayers():
    def __init__(self):
        self.player_list = []
        self.teams_df = None
        self.player_picked_league_count = {}
        self.current_points_dict = {}
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
        
    def get_all_epl_players(self):
        regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        req = self.request_error_check(regUrl)
        
        elements_df = pd.DataFrame(req['elements'])
        elements_types_df = pd.DataFrame(req['element_types'])
        self.teams_df = pd.DataFrame(req['teams'])

        slim_elements_df = elements_df[['id','second_name','first_name','team','event_points','form','element_type',
                                        'selected_by_percent','now_cost','minutes','transfers_in','transfers_out','value_season','total_points']]
        slim_elements_df['position'] = slim_elements_df.element_type.map(elements_types_df.set_index('id').singular_name_short)
        slim_elements_df['team'] = slim_elements_df.team.map(self.teams_df.set_index('id').short_name)
        return slim_elements_df

    def set_team_player_list(self, gw):
        slim_elements_df = self.get_all_epl_players()
        
        req = self.request_error_check('https://fantasy.premierleague.com/api/leagues-classic/982237/standings/')
        
        league = pd.DataFrame(req['standings']['results'])
        for i in league.index:
            req = self.request_error_check(f"https://fantasy.premierleague.com/api/entry/{league['entry'][i]}/event/{gw}/picks/")
            
            self.set_player_picked_league_count(req['picks'])
            
            user = pd.DataFrame(req['picks'])
            user = user.rename(columns={"element":"id","position": "team_position"})
            user = user.merge(slim_elements_df, on="id", how="left")
            
            fixtures_df = self.set_fixtures_df(user['id'])
            user = user.merge(fixtures_df[['id','difficulty', 'opponent', 'is_home', 'event', 'prev_opponent', 'prev_difficulty', 'prev_is_home']], on="id", how="left")
            
            difficulty_color = {1: 'background-color: #375523; color: white;', 2: 'background-color: #01fc7a; color:black;', 3: 'background-color: #e7e7e7; color: black;', 4: 'background-color: #ff1751; color:white;', 5: 'background-color: #80072d; color: white;'}
            user['opponent_diff_style'] = user.difficulty.map(difficulty_color)
            user['prev_opponent_diff_style'] = user.prev_difficulty.map(difficulty_color)
            
            if req['automatic_subs']:
                subs = pd.DataFrame(req['automatic_subs'])
                user['sub_in'] = np.where(user['id']==subs['element_in'][0], True, False)
                user['sub_out'] = np.where(user['id']==subs['element_out'][0], True, False)
            else:
                user['sub_in'] = False
                user['sub_out'] = False
            
            user['event_points_multi'] = user['event_points'] * user['multiplier']
            self.current_points_dict[league['entry'][i]] = int(user.iloc[:11, user.columns.get_indexer(['event_points_multi'])].sum().values[0])
            self.player_list.append({'team_name': league['entry_name'][i], 'team_id': league['entry'][i], 'gw':gw, 
                                    'is_current_gw': (gw == user.event[0]), 'players': user.T.to_dict().values()})

    def set_fixtures_df(self, player_picks):
        fixtures_df = pd.DataFrame()
        for player_id in player_picks:
            req = self.request_error_check(f"https://fantasy.premierleague.com/api/element-summary/{player_id}/")
            
            single_fixture = pd.DataFrame(req['fixtures'][0], index=[0])
            single_fixture['player_id'] = player_id
            
            hist = pd.DataFrame(req['history'][-1], index=[0])
            hist['prev_opponent'] = hist.opponent_team.map(self.teams_df.set_index('id').short_name)
            hist['prev_difficulty'] = hist.opponent_team.map(self.teams_df.set_index('id').strength)
            hist = hist.rename(columns={"was_home": "prev_is_home", 'element': 'player_id'})
            single_fixture = single_fixture.merge(hist[['player_id','prev_opponent', 'prev_difficulty', 'prev_is_home']], on="player_id", how="left")
            
            
            fixtures_df = fixtures_df.append(single_fixture, ignore_index = True )

        fixtures_df = fixtures_df.drop(['id'], axis=1).rename({'player_id': 'id'}, axis=1)
        
        
        fixtures_df['opponent'] = np.where(fixtures_df['is_home'] == True, fixtures_df.team_a.map(self.teams_df.set_index('id').short_name), fixtures_df.team_h.map(self.teams_df.set_index('id').short_name))
        return fixtures_df

    def set_player_picked_league_count(self, picks):
        player_picks_list = [i['element'] for i in picks]
            
        for player_id in player_picks_list:
            if player_id in self.player_picked_league_count:
                self.player_picked_league_count[player_id] += 1
            else:
                self.player_picked_league_count[player_id] = 1
                
    def get_team_player_list(self):
        return self.player_list
    
    def get_player_picked_league_count(self):
        return self.player_picked_league_count

    def get_player_picked_league_percent(self, member_count):
        return {player_id: int((count/member_count)*100) for player_id, count in self.player_picked_league_count.items()}
    
    def subtract_tranfer_hits_from_current_points(self, league_list):
        for i in league_list:
            self.current_points_dict[i['team_id']] -= i['gw_transfer_cost'][-1]
    
    def get_current_points(self):
        return self.current_points_dict
