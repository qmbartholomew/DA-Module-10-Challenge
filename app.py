# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
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
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Last 12 months of precipitation data<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of all weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Temperature observations from the most active station<br/><br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"- Min, Avg, and Max temperatures from the start date (yyyy-mm-dd)<br/><br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"- Min, Avg, and Max temperatures from start to end date (yyyy-mm-dd)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Resolve threading issues with SQLite
    session = get_session()
    """Return JSON of date and precipitation for last 12 months"""
    # Calculate the date one year ago from the last data point (2017-08-23)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query date and precipitation from the last year
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()

    # Convert results to dictionary {date: prcp}
    precip_data = {date: prcp for date, prcp in results}

    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    # Resolve threading issues with SQLite
    session = get_session()
    """Return a JSON list of all station IDs"""
    # Query all station IDs
    results = session.query(Station.station).all()

    # Unravel results into a flat list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Resolve threading issues with SQLite
    session = get_session()
    """Return a JSON list of temperature observations for the previous year from the most active station"""
    # Define the most active station ID
    most_active_station = "USC00519281"

    # Calculate the date one year ago from 2017-08-23
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the temperature observations
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago)\
        .order_by(Measurement.date).all()

    # Convert results to a list of dicts (optional formatting)
    temps = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Resolve threading issues with SQLite
    session = get_session()
    """Return TMIN, TAVG, TMAX for all dates >= start date"""
    # Query temperature stats from start to end of dataset
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Format results as dictionary
    temps = {
        "Start Date": start,
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 1),
        "TMAX": results[0][2]
    }

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Resolve threading issues with SQLite
    session = get_session()
    """Return TMIN, TAVG, TMAX between start and end date inclusive"""
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start)\
     .filter(Measurement.date <= end).all()

    temps = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 1),
        "TMAX": results[0][2]
    }

    return jsonify(temps)

def get_session():
    return Session(engine)

if __name__ == "__main__":
    app.run(debug=True)