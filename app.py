import pandas as pd
from flask import Flask, render_template, request
from flask_paginate import Pagination

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/powerplants")
def powerplants():
    # Convert the CSV to a list of dicts
    df = pd.read_csv("powerplants.csv")
    powerplants = df.to_dict('records')

    # Let's only send 20 for now
    PER_PAGE = 20
    current_page = int(request.args.get('page', 1))
    start = PER_PAGE * current_page - PER_PAGE
    end = PER_PAGE * current_page

    powerplants = powerplants[start:end]

    pagination = Pagination(total=df.shape[0],
                            page=current_page,
                            per_page=PER_PAGE)


    # Send the dicts to the page
    return render_template(
        'powerplants.html',
        powerplants=powerplants,
        pagination=pagination
    )

@app.route("/powerplants/<int:plant_id>")
def powerplant(plant_id):
    df = pd.read_csv("powerplants.csv")
    matching_rows = df[df['Plant_Code'] == plant_id]

    plant = matching_rows.to_dict('records')[0]

    return render_template(
        'powerplant.html',
        plant=plant
    )

@app.route("/states/<string:state_name>")
def by_state(state_name):
    # Open the CSV and filter
    df = pd.read_csv("powerplants.csv")
    matching_rows = df[df['StateName'] == state_name]

    # Convert to a list of dicts
    powerplants = matching_rows.to_dict('records')

    # Send all of the power plants to a new template
    # also send the state name!
    return render_template(
        'state.html',
        state_name=state_name,
        powerplants=powerplants
    )
