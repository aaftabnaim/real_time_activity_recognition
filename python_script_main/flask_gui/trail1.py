import time
import os
from flask import Flask,flash,redirect,\
     render_template,request,session,abort

app = Flask(__name__)
@app.route("/")

parent_file_path = os.path.dirname(os.path.abspath(__file__))

def hello():
    return "Hello Aaftab!"

@app.route("/today")
def today():
        
    
    return "Hello Aaftab!This is how well you are doing today"


@app.route("/uptodate")
def alltime():
    return "Hello Aaftab!Your performance to date"


@app.route("/history/<string:name>/")
def history(name):
    return render_template('test.html',name=name)


if __name__=='__main__':
    app.run()
