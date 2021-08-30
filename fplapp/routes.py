from flask import Flask, render_template, url_for, request, flash, redirect

from fplapp import app
from fplapp import fpl
import json

@app.route('/', methods=['GET','POST'])
def home():
    temp = [{'name': 'Taylor Smith',
            'player_history': [{'bank': 2.5,
                                'gw': 1,
                                'gw_bench_points': 2,
                                'gw_points': 78,
                                'gw_transfer_cost': 0,
                                'gw_transfers': 0,
                                'overall_rank': 2440789,
                                'rank': 2440791,
                                'rank_sort': 2521287,
                                'team_value': 100.0,
                                'total_points': 78},
                                {'bank': 2.5,
                                'gw': 2,
                                'gw_bench_points': 2,
                                'gw_points': 56,
                                'gw_transfer_cost': 0,
                                'gw_transfers': 0,
                                'overall_rank': 2316788,
                                'rank': 3565554,
                                'rank_sort': 3614550,
                                'team_value': 100.2,
                                'total_points': 134}],
            'team_id': 4498973,
            'team_name': 'AyewPlaynWilfMatetas'},
            {'name': 'Becca Dellenbaugh',
            'player_history': [{'bank': 0.5,
                                'gw': 1,
                                'gw_bench_points': 18,
                                'gw_points': 72,
                                'gw_transfer_cost': 0,
                                'gw_transfers': 0,
                                'overall_rank': 3109336,
                                'rank': 3109341,
                                'rank_sort': 3166388,
                                'team_value': 100.0,
                                'total_points': 72},
                                {'bank': 0.0,
                                'gw': 2,
                                'gw_bench_points': 22,
                                'gw_points': 63,
                                'gw_transfer_cost': 4,
                                'gw_transfers': 2,
                                'overall_rank': 2620881,
                                'rank': 2420759,
                                'rank_sort': 2429124,
                                'team_value': 100.0,
                                'total_points': 131}],
            'team_id': 3467778,
            'team_name': 'No Kane, No Gain'},
            {'name': 'David Dellenbaugh',
            'player_history': [{'bank': 0.5,
                                'gw': 1,
                                'gw_bench_points': 18,
                                'gw_points': 75,
                                'gw_transfer_cost': 0,
                                'gw_transfers': 0,
                                'overall_rank': 2781506,
                                'rank': 2781510,
                                'rank_sort': 2882037,
                                'team_value': 100.0,
                                'total_points': 75},
                                {'bank': 0.5,
                                'gw': 2,
                                'gw_bench_points': 10,
                                'gw_points': 51,
                                'gw_transfer_cost': 0,
                                'gw_transfers': 0,
                                'overall_rank': 2969469,
                                'rank': 4549188,
                                'rank_sort': 4618549,
                                'team_value': 100.1,
                                'total_points': 126}],
            'team_id': 6034219,
            'team_name': 'Beaglemania 2'}]
    
    data = []
    for j in temp:
        t = {'name': j['name'], 'gw': [0], 'gw_points':[0],'total_points': [0], 'gw_bench_points': [0], 'total_bench_points': [0], 
            'gw_transfer_cost': [0], 'total_transfer_cost': [0], 'gw_transfers': [0], 'total_transfers': [0],'team_value': [0]}
        for i in j['player_history']:
            t['gw'].append(int(i['gw']))
            t['gw_points'].append(int(i['gw_points']))
            t['total_points'].append(int(i['total_points']))
            t['gw_bench_points'].append(int(i['gw_bench_points']))
            t['total_bench_points'].append(sum(t['total_bench_points']) + i['gw_bench_points'])
            t['gw_transfer_cost'].append(i['gw_transfer_cost'])
            t['total_transfer_cost'].append(sum(t['total_transfer_cost']) + i['gw_transfer_cost']) 
            t['gw_transfers'].append(sum(t['gw_transfers']) + i['gw_transfers'])
            t['team_value'].append(i['team_value'])
            
        data.append(t)
    return render_template('home.html', data = json.dumps(data))

@app.route('/selectteam', methods=['GET', 'POST'])
def selectteam():
    if request.method == 'POST':
        
        
        request_user_ID = request.form["userID"] 
        
        league_info =  fpl.get_user_leagues_info(request_user_ID)
        if league_info == False:
            flash('Oh no something went wrong. Please try again!', 'danger')
            return redirect(url_for('home'))
        else:
            return render_template('selectteam.html', league_info = league_info) 

@app.route('/check-data', methods=['GET', 'POST'])
def process_data():
    if request.method == 'POST':
        
        
        rank = int(request.form['select_league'])
        response = ''
        if rank == 1:
            response = 'YES'
        elif rank > 1 and rank <= 5:
            response = 'NO'
        elif rank > 5:
            response = 'LOL'

        print(rank)
        return render_template('amiwinning.html', rank_response = response)
    
    