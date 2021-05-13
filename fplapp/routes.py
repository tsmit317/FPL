from flask import Flask, render_template, url_for, request, flash, redirect

from fplapp import app
from fplapp import fpl

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/selectteam', methods=['GET', 'POST'])
def selectteam():
    if request.method == 'POST':
        
        
        request_league_ID = request.form["leagueID"] 
        
        members =  fpl.get_league_teams(request_league_ID)
       
        return render_template('selectteam.html', leagueMembers = members) 