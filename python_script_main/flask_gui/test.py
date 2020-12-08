import os
import numpy as np

parent_file_path = os.path.dirname(os.path.abspath(__file__))
split_parent_path = parent_file_path.split('/')
parent_dir = "/".join(split_parent_path[:-1])

folder_paths = [x[0] for x in os.walk\
                ("/home/pi/Desktop/myActivityRecognition/capture")]


dates = [i.split("/")[-1] for i in folder_paths[1:]]

print(dates)

path = '/home/pi/Desktop/myActivityRecognition/capture/Sat_05_12_2020/status.csv'

import matplotlib.pyplot as plt
import pandas as pd
classes = ['eating', 'none', 'praying', 'sleeping', 'studying']


data = pd.read_csv(path)

values = []

for i in range(len(classes)):
    values.append(data[classes[i]].sum())



barplot = plt.bar(classes,values)
plt.savefig("/home/pi/Desktop/myActivityRecognition/flask_gui/static/graph.png")
    
