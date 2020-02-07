import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations and corresponding prcp values"""
    # Query precipitation values for all dates
    results = session.query(Measurement.date, Measurement.prcp).all()

    results_dict = {}
    for result in results:
        results_dict[result[0]] = result[1]

    session.close()

    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data"""
    # Query all passengers
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def temperatures():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data"""
    last_data_point_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_data_point_date = dt.date.fromisoformat(last_data_point_date_result[0])
    one_year_ago_from_last_data_point_date = last_data_point_date - dt.timedelta(days=365)

    # Perform a query to retrieve the temperature observations
    temperature_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago_from_last_data_point_date.strftime("%Y-%m-%d")).filter(Measurement.date <= last_data_point_date.strftime("%Y-%m-%d")).all()

    temperatures = []
    for temperature_result in temperature_results:
        temperatures.append({temperature_result[0]: temperature_result[1]})

    session.close()

    return jsonify(temperatures)

@app.route("/api/v1.0/<start>", defaults={"end": dt.datetime.now().strftime("%Y-%m-%d")})
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start or start-end range."""

    temperature_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    if temperature_results:
        return jsonify(temperature_results)

    return jsonify({"error": f"Temperature data for dates between {start} and {end} not found."}), 404



if __name__ == '__main__':
    app.run(debug=True)
