import pandas as pd
import requests
import numpy as np

class FplPlayers():
    def __init__(self):
        self.player_list = []
        self.teams_df = None
        
    def get_all_epl_players(self):
        regUrl = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        req = requests.get(regUrl)
        if req.status_code != 404:
            r = req.json()
            
        elements_df = pd.DataFrame(r['elements'])
        elements_types_df = pd.DataFrame(r['element_types'])
        self.teams_df = pd.DataFrame(r['teams'])

        slim_elements_df = elements_df[['id','second_name','first_name','team','event_points','form','element_type',
                                        'selected_by_percent','now_cost','minutes','transfers_in','transfers_out','value_season','total_points']]
        slim_elements_df['position'] = slim_elements_df.element_type.map(elements_types_df.set_index('id').singular_name_short)
        slim_elements_df['team'] = slim_elements_df.team.map(self.teams_df.set_index('id').short_name)
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

            user = pd.DataFrame(r['picks'])
            user = user.rename(columns={"element":"id","position": "team_position"})
            user = user.merge(slim_elements_df, on="id", how="left")
            
            fixtures_df = self.set_fixtures_df(user['id'])
            user = user.merge(fixtures_df[['id','difficulty', 'opponent']], on="id", how="left")
            
            self.player_list.append({'team_name': league['entry_name'][i], 'team_id': league['entry'][i], 'players': user.T.to_dict().values()})

    def set_fixtures_df(self, player_picks):
        fixtures_df = pd.DataFrame()
        for player_id in player_picks:
            regUrl = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
            req = requests.get(regUrl)
            if req.status_code != 404:
                r = req.json()

            single_fixture = pd.DataFrame(r['fixtures'][0], index=[0])
            single_fixture['player_id'] = player_id
            fixtures_df = fixtures_df.append(single_fixture, ignore_index = True )

        fixtures_df = fixtures_df.drop(['id'], axis=1).rename({'player_id': 'id'}, axis=1)
        fixtures_df['opponent'] = np.where(fixtures_df['is_home'] == True, fixtures_df.team_a.map(self.teams_df.set_index('id').short_name), fixtures_df.team_h.map(self.teams_df.set_index('id').short_name))
        return fixtures_df

    def get_team_player_list(self):
        return self.player_list

