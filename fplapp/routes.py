from flask import Flask, render_template, url_for, request, flash, redirect

from fplapp import app
from fplapp import fpl
import json

@app.route('/', methods=['GET','POST'])
def home():
    data = fpl.create_fpl_list(982237)
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
    
    