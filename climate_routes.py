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
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

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
    twelve_mo_data = engine.execute("SELECT date,tobs FROM Measurement WHERE date<= '" + highest_date[0] + "' AND     date>= '" + str(year_from_highest) + "' ORDER BY date desc")
    all_temperatures = []
    for rec in twelve_mo_data:
        temp_dict = {}
        temp_dict["date"] = rec.date
        temp_dict["tobs"] = rec.tobs
        all_temperatures.append(temp_dict)

    return jsonify(all_temperatures)

@app.route("/api/v1.0/start")
def tobs_start():
    
    date = request.args.get('start')
    print(str(request.query_string))

    #dateresult = datetime.strptime(date, '%Y-%m-%d')

    #start_temp_list = engine.execute("SELECT MIN(tobs) AS MinTemp, MAX(tobs) AS MaxTemp, AVG(tobs) AS AvgTemp FROM Measurement WHERE date >= '" + date + "'")

    #for rec in start_temp_list:
       #print(rec)
    
    return request.query_string
   
@app.route("/api/v1.0/start/end")
def tobs_start_end():
    
    #start_end_list = engine.execute("SELECT MIN(tobs) AS MinTemp, MAX(tobs) AS MaxTemp, AVG(tobs) AS AvgTemp FROM Measurement WHERE date >= '2016-08-18' AND date <= '2017-08-18'")
    #for rec in start_end_list:
       #print(rec)
    
    return request.query_string
    
if __name__ == '__main__':
    app.run(debug=True)
