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

    all_precipitation = []
    for date, prcp in precip_list:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation (inches)"] = prcp
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
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    ".first we build the subquery for the filter...."
    subquery = session.query(Measurement.station.label("Station")).\
          group_by(Measurement.station).\
          order_by(desc(func.count(Measurement.station))).first() 

    # Find the most recent date in the Measurement table for the one station
    maxdate = session.query(func.max(Measurement.date)).\
    filter(Measurement.station.in_(subquery)).all() 
    
    date_time_obj = dt.datetime.strptime(maxdate[0][0],'%Y-%m-%d')

    year_earlier = date_time_obj - dt.timedelta(days=366) 

    """Return a list of temperature data including the date for the one location"""
    # Query all measurements
    temp_list = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_earlier).\
    filter(Measurement.station.in_(subquery)).group_by(Measurement.date).order_by(Measurement.date).all()    

    session.close()

    all_temps = []
    for date, tobs in temp_list:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature (F)"] = tobs
        all_temps.append(tobs_dict)
    
    return jsonify(all_temps)


###############################################


    
    return jsonify(query_data)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # work with the date
    # convert the string to a datetime obj

    date_start_obj = dt.datetime.strptime(start,'%Y-%m-%d')
       
    # this is the main query to calculate the min, max, avg with func... 
        
    temp_list = session.query(func.min(Measurement.tobs).label("Min_Temp"), \
        func.avg(Measurement.tobs).label("Avg_Temp"), \
        func.max(Measurement.tobs).label("Max_Temp")).\
        filter(Measurement.date >= date_start_obj).all()
    
    all_temps = []
    for Min_Temp, Avg_Temp, Max_Temp in temp_list:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = Min_Temp
        temp_dict["Average Temperature"] = Avg_Temp
        temp_dict["Maximum Temperature"] = Max_Temp
        all_temps.append(temp_dict)

    session.close()

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # work with the date
    # convert the string to a datetime obj

    date_start_obj = dt.datetime.strptime(start,'%Y-%m-%d')
    date_end_obj = dt.datetime.strptime(end,'%Y-%m-%d')
    
    # this is the main query to calculate the min, max, avg with func... 
        
    temp_list = session.query(func.min(Measurement.tobs).label("Min_Temp"), \
        func.avg(Measurement.tobs).label("Avg_Temp"), \
        func.max(Measurement.tobs).label("Max_Temp")).\
        filter(Measurement.date >= date_start_obj).\
        filter(Measurement.date <= date_end_obj).all()
    
    all_temps = []
    for Min_Temp, Avg_Temp, Max_Temp in temp_list:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = Min_Temp
        temp_dict["Average Temperature"] = Avg_Temp
        temp_dict["Maximum Temperature"] = Max_Temp
        all_temps.append(temp_dict)

    session.close()

    return jsonify(all_temps)


if __name__ == '__main__':
    app.run(debug=True)
