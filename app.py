from flask import Flask, request, render_template
import pandas as pd
import gzip
import pickle
from datetime import date

app = Flask(__name__)


filepath = "model.pkl"
with gzip.open(filepath, 'rb') as f:
    p = pickle.Unpickler(f)
    rf = p.load()

# Functions
column = ['days_left', 'airline_AirAsia', 'airline_GO FIRST',
          'airline_Indigo', 'airline_Other', 'airline_SpiceJet',
          'airline_Vistara', 'dep_time_Early Morning', 'dep_time_Evening',
          'dep_time_Late Night', 'dep_time_Morning', 'dep_time_Night',
          'from_Chennai', 'from_Delhi', 'from_Hyderabad', 'from_Kolkata',
          'from_Mumbai', 'stop_1', 'stop_2+', 'to_Chennai', 'to_Delhi',
          'to_Hyderabad', 'to_Kolkata', 'to_Mumbai', 'class_Economy',
          'duration_Medium', 'duration_Short']


def class_fun(cl):
    class_dict = {"Economy": "class_Economy",
                  "Business": 0}
    return class_dict.get(cl, -1)


def time_fun(tim):
    time_dict = {
        "Early Morning": "dep_time_Early Morning",
        "Evening": "dep_time_Evening",
        "Late Night": "dep_time_Late Night",
        "Morning": "dep_time_Morning",
        "Night": "dep_time_Night",
        "Afternoon": 0
    }

    return time_dict.get(tim, -1)


def duration_fun(dur):
    duration_dict = {"Medium": "duration_Medium",
                     "Short": "duration_Short",
                     "Long": 0}
    return duration_dict.get(dur, -1)


def stop_fun(stop):
    stop_dict = {"1": "stop_1",
                 "2+": "stop_2+",
                 "0": 0}
    return stop_dict.get(stop, -1)


def airline_fun(airline):
    airline_dict = {
        "AirAsia": "airline_AirAsia",
        "Go First": "airline_GO FIRST",
        "Indigo": "airline_Indigo",
        "Other": "airline_Other",
        "SpiceJet": "airline_SpiceJet",
        "Vistara": "airline_Vistara",
        "Air India": 0

    }

    return airline_dict.get(airline, -1)


def source_fun(source):
    source_dict = {
        "Delhi": "from_Delhi",
        "Mumbai": "from_Mumbai",
        "Kolkata": "from_Kolkata",
        "Chennai": "from_Chennai",
        "Hyderabad": "from_Hyderabad",
        "Bangalore": 0
    }

    return source_dict.get(source, -1)


def destination_fun(destination):
    destination_dict = {
        "Delhi": "to_Delhi",
        "Mumbai": "to_Mumbai",
        "Kolkata": "to_Kolkata",
        "Chennai": "to_Chennai",
        "Hyderabad": "to_Hyderabad",
        "Bangalore": 0
    }

    return destination_dict.get(destination, -1)


def days_fun(month, day):
    days = int(str(date(2022, int(month), int(day)) - date.today()).split()[0])
    return days


@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        source = request.form['from']
        destination = request.form['to']
        month = request.form['month']
        day = request.form['day']
        time = request.form['time']
        airline = request.form['airline']
        duration = request.form['duration']
        stop = request.form['stop']
        cla = request.form['class']

    df_predict = pd.DataFrame([[0]*len(column)], columns=column)

    cl = class_fun(cla)
    tim = time_fun(time)
    dur = duration_fun(duration)
    des = destination_fun(destination)
    sou = source_fun(source)
    sto = stop_fun(stop)
    air = airline_fun(airline)
    days_left = days_fun(month, day)

    if ((cl == -1) | (tim == -1) | (dur == -1) | (des == -1) | (sou == -1) | (sto == -1) | (air == -1)):
        return render_template('index.html', prediction_text="Invalid Input")

    if (destination == source):
        return render_template('index.html', prediction_text="Source and Destination City cannot be the same")

    if (days_left < 0):
        return render_template('index.html', prediction_text="Select Future Date")

    if sto != 0:
        df_predict[sto] = 1
    if cl != 0:
        df_predict[cl] = 1
    if tim != 0:
        df_predict[tim] = 1
    if dur != 0:
        df_predict[dur] = 1
    if des != 0:
        df_predict[des] = 1
    if sou != 0:
        df_predict[sou] = 1
    if air != 0:
        df_predict[air] = 1
    df_predict['days_left'] = days_left

    pred = round(rf.predict(df_predict)[0], 2)
    return render_template('index.html', prediction_text=f"Price : Rs {pred}")


if __name__ == "__main__":
    app.run(debug=True)
