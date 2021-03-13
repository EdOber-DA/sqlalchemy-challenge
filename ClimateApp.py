import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, desc

from flask import Flask, jsonify
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(inspect(engine).get_table_names())
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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the Measurement table.
    maxdate = session.query(func.max(Measurement.date)).all() 
    
    date_time_obj = dt.datetime.strptime(maxdate[0][0],'%Y-%m-%d')

    year_earlier = date_time_obj - dt.timedelta(days=366) 

    """Return a list of precipitation data including the date and amount"""
    # Query all measurements
    precip_list = session.query(Measurement.date, func.sum(Measurement.prcp)).\
    filter(Measurement.date >= year_earlier).\
    group_by(Measurement.date).order_by(Measurement.date).all()    

    session.close()

    # precip_df = pd.DataFrame(precip_list).set_index("date").sort_values(by="date")

    all_precipitation = []
    for date, prcp in precip_list:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precipitation.append(precip_dict)
    
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def passengers():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    all_stations = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations_list = list(np.ravel(all_stations))

    return jsonify(all_stations_list)


@app.route("/api/v1.0/tobs")
def tobs():

    return jsonify()


@app.route("/api/v1.0/<start>")
def start():

    return jsonify()

@app.route("/api/v1.0/<start>/<end>")
def start_end():

    return jsonify()


if __name__ == '__main__':
    app.run(debug=True)
