import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    """Return a dictionary of date and prcp values"""
    results = session.query(Measurement.date, Measurement.prcp).order_by((Measurement.date).desc()).all()

    # Create a dictionary from the row data and append to a list of measures
    all_measures = []
    for date, prcp in results:
        measure_dict = {}
        measure_dict["date"] = date
        measure_dict["prcp"] = prcp
        all_measures.append(measure_dict)

    return jsonify(all_measures)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    list_of_stations = engine.execute("SELECT name FROM Station")

    return jsonify({'list_of_stations': [dict(row) for row in list_of_stations]})
    
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of Tobs"""
    # Calculate the last data point from the list of Measurements for this station
    highest_data_point = engine.execute("SELECT MAX(date) FROM Measurement ORDER BY date desc")
    for rec in highest_data_point:
       highest_date = rec
    
    # Convert the highest data point result from string to datetime format
    highestresult = datetime.strptime(highest_date[0], '%Y-%m-%d')
    
    # Calculate the date 12 months ago from the highest data point
    year_from_highest = highestresult - timedelta(days = 365)

    # Build the data frame with the 12 months of temperature data
    twelve_mo_data = engine.execute("SELECT date,tobs FROM Measurement WHERE date<= '" + highest_date[0] + "' AND date>= '" + str(year_from_highest) + "' ORDER BY date desc")
    all_temperatures = []
    for rec in twelve_mo_data:
        temp_dict = {}
        temp_dict["date"] = rec.date
        temp_dict["tobs"] = rec.tobs
        all_temperatures.append(temp_dict)

    return jsonify(all_temperatures)

@app.route("/api/v1.0/<start>")
def tobs_start(start):
    start_tobs_list = engine.execute("SELECT MIN(tobs) AS MinTemp, MAX(tobs) AS MaxTemp, AVG(tobs) AS AvgTemp FROM Measurement WHERE date>= '" + start + "' ORDER BY date desc")
    start_averages = []
    for rec in start_tobs_list:
        avg_dict = {}
        avg_dict["min"] = rec.MinTemp
        avg_dict["max"] = rec.MaxTemp
        avg_dict["avg"] = rec.AvgTemp
        start_averages.append(avg_dict)
    
    return jsonify(start_averages)
   
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start,end):
    
    start_end_list = engine.execute("SELECT MIN(tobs) AS MinTemp, MAX(tobs) AS MaxTemp, AVG(tobs) AS AvgTemp FROM Measurement WHERE date >= '" + start + "' AND date <= '" + end + "' ORDER BY date desc")
    start_end_averages = []
    for rec in start_end_list:
        avg_end_dict = {}
        avg_end_dict["min"] = rec.MinTemp
        avg_end_dict["max"] = rec.MaxTemp
        avg_end_dict["avg"] = rec.AvgTemp
        start_end_averages.append(avg_end_dict)
    
    return jsonify(start_end_averages)
    
if __name__ == '__main__':
    app.run(debug=True)
