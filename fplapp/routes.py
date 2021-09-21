from flask import Flask, render_template, url_for, request, flash, redirect

from fplapp import app
from fplapp.fpl_data import FplData
import json


@app.route('/', methods=['GET','POST'])
def home():
    fpl_data = FplData()
    fpl_data.create_fpl_list(982237)
    data = fpl_data.get_league_data()
    if type(data[0]) is dict:
        
        return render_template('home.html', data = json.dumps(data), league_info= data, chip_dict=fpl_data.get_chip_count(), chip_used_list = fpl_data.get_chips_used_list(),
                                most_points_single_gw = fpl_data.get_most_points_scored_in_a_gw(), max_points_per_gw = fpl_data.get_max_points_per_gw(),
                                count_gw_leader=fpl_data.count_gw_leader(), min_points_per_gw=fpl_data.get_min_points_per_gw(),
                                count_gw_lowest=fpl_data.count_gw_lowest())
    else:
        return render_template('errorpage.html', error_message = data)


# @app.route('/selectteam', methods=['GET', 'POST'])
# def selectteam():
#     if request.method == 'POST':
        
#         request_user_ID = request.form["userID"] 
        
        
#         if league_info == False:
#             flash('Oh no something went wrong. Please try again!', 'danger')
#             return redirect(url_for('home'))
#         else:
#             return render_template('selectteam.html', league_info = league_info) 


# Currently not being used 
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
    

