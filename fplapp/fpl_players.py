import pandas as pd
import requests
import numpy as np

class FplPlayers():
    def __init__(self):
        self.player_list = []
        
    def get_all_epl_players(self):
        regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        req = requests.get(regUrl)
        if req.status_code != 404:
            r = req.json()
            
        elements_df = pd.DataFrame(r['elements'])
        elements_types_df = pd.DataFrame(r['element_types'])
        teams_df = pd.DataFrame(r['teams'])

        slim_elements_df = elements_df[['id','second_name','first_name','team','event_points','form','element_type','selected_by_percent','now_cost','minutes','transfers_in','transfers_out','value_season','total_points']]
        slim_elements_df['position'] = slim_elements_df.element_type.map(elements_types_df.set_index('id').singular_name_short)
        slim_elements_df['team'] = slim_elements_df.team.map(teams_df.set_index('id').name)
        return slim_elements_df

    def set_team_player_list(self, gw):
        slim_elements_df = self.get_all_epl_players()
        url = 'https://fantasy.premierleague.com/api/leagues-classic/982237/standings/'
        req = requests.get(url)
        if req.status_code != 404:
            r = req.json()

        league = pd.DataFrame(r['standings']['results'])


        
        for i in league.index:
            regUrl = f"https://fantasy.premierleague.com/api/entry/{league['entry'][i]}/event/{gw}/picks/"
            req = requests.get(regUrl)
            if req.status_code != 404:
                r = req.json()
            r.keys()

            user = pd.DataFrame(r['picks'])
            user2 = user.rename(columns={"element":"id","position": "team_position"})
            to_dict = user2.merge(slim_elements_df, on="id", how="left")
            self.player_list.append({'team_name': league['entry_name'][i], 'players': to_dict.T.to_dict().values()})
        
    def get_team_player_list(self):
        return self.player_list

