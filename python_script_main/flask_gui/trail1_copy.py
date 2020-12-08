import time
import os
import pandas as pd
from flask import Flask,flash,redirect,\
     render_template,request,session,abort
import matplotlib.pyplot as plt


classes = ['eating', 'none', 'praying', 'sleeping', 'studying']
parent_file_path = os.path.dirname(os.path.abspath(__file__))
split_parent_path = parent_file_path.split('/')
parent_dir = "/".join(split_parent_path[:-1])
app = Flask(__name__)
@app.route("/")
def hello():
    path = parent_dir+'/capture/'
    folder_paths = [x[0] for x in os.walk(path)]    
    dates = [i.split("/")[-1] for i in folder_paths[1:]]
    #sort the list in descending order i.e. latest first
    return render_template('dashboard.html', history=dates)

@app.route("/today")
def display_today():

    today_date_str = time.strftime("%a_%d_%m_%Y")
    status_csv_path = parent_dir + "/capture/" + today_date_str + "/status.csv"
    data = pd.read_csv(status_csv_path)
    eat_IN = data[classes[0]].sum()
    none_IN = data[classes[1]].sum()
    pray_IN = data[classes[2]].sum()
    sleep_IN = data[classes[3]].sum()
    study_IN = data[classes[4]].sum()
    return render_template('test.html', eat = eat_IN, none_ = none_IN, pray=pray_IN, sleep=sleep_IN, study=study_IN)

@app.route("/uptodate")
def alltime():
    return "Hello Aaftab!Your performance to date"


@app.route("/history/<string:name>/")
def history(name):
    status_csv_path = parent_dir + "/capture/" + name + "/status.csv"
    data = pd.read_csv(status_csv_path)
    values = [data[classes[i]].sum() for i in range(len(classes))]
    eat_IN = values[0]
    none_IN = values[1]
    pray_IN = values[2]
    sleep_IN = values[3]
    study_IN = values[4]

    barplot = plt.bar(classes,values)
    save_path = parent_dir+"/flask_gui/static/"+name+".png"
    plt.savefig(save_path)
    plt.close()
    return render_template('day.html',name=name, eat = eat_IN, none_ = none_IN, pray=pray_IN, sleep=sleep_IN, study=study_IN)



if __name__=='__main__':
    app.run()

