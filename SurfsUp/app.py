# Import the dependencies.

import numpy as np

import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

app = Flask(__name__)

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/r>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    # Calculate the date one year ago from the last data point in the data
    session = Session(engine)
    julianyear_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # query precipitation for the last year
    outcome = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= oneyear).order_by(Measurement.date).all()
    
    #create a dictionary and return the JSON rep
    precip_dict = dict(outcome)
    return jsonify(precip_dict)

    
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations = session.query(Station.station).all()

    # Extract station names from the query results
    all_stations = [station[0] for station in stations]

    #Return a JSON list of stations from the dataset
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the last date in the data
    recentdata = dt.date(2017,8,23)
    julianyear = recentdata-dt.timedelta(days=365)
    
    #Query dates andt temp 
    outcome = session.query(measurement.tobs)\
                            .filter(measurement.station=="USC00519281")\
                            .filter(measurement.date>=julianyear)\
                            .all()
    
    temp_obs = [{"date": date, "tobs": tobs} for date, tobs in outcome]

    #Return all in format JSON from last year
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def start(start):
    #convert the string into a datetime object
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")

    #Query the database
    temperature = session.query(func.min(measurement.tobs), 
                            func.max(measurement.tobs),
                            func.round(func.avg(Measurement.tobs))).\
                            filter(Measurement.date >= start_date).all()
                            
    #extract the results and return in JSON format
    outcome = list(np.ravel(temperature))
    return jsonify(outcome)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    #convert the string into a datetime object
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")
   
    #Query the database
    temperature = session.query(func.min(measurement.tobs), 
                            func.max(measurement.tobs),
                            func.round(func.avg(Measurement.tobs))).\
                            filter(Measurement.date.between(start_date,end_date)).all()
                  
    #extract the results and return in JSON format
    outcome = list(np.ravel(temperature))
    return jsonify(outcome)


if __name__ == "__main__":
    app.run(debug=True)