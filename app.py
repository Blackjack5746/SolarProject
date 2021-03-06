# -*- coding: utf-8 -*-
"""
Created on Sat Aug  7 16:50:52 2021

@author: Blackjack
"""

from flask import Flask, render_template, request, jsonify
import requests 
import json
from tensorflow.keras import layers, models
import tensorflow as tf 
import pandas as pd
import numpy as np

app = Flask(__name__)
tf.keras.models.load_model("model2.pkl")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/Details")
def details():
    return render_template("details.html")

@app.route("/Gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/About")
def about():
    return render_template("about.html")

@app.route("/predict")  
def Predict():
    req = requests.get('https://api.thingspeak.com/channels/1447918/feeds.json?api_key=9XU54S4EIC3I8110&results=1')
    our_data = json.loads(req.content)
    Air = our_data['feeds']
    Moya = Air[0]
    air_temp = round(float(Moya['field1']), 5)
    rel_hum  = round(float(Moya['field2']), 5)
    mod_temp = round(float(Moya['field3']), 5)
    Dust     = round(float(Moya['field4']), 5)
    atm_pres = round(float(Moya['field5']), 5)
    CO_gas   = round(float(Moya['field6']), 5)
    power    = round(abs(float(Moya['field7'])), 5)
    random_dict = {"field1": air_temp, "field2": rel_hum, "field3": mod_temp}
    
    if mod_temp < -20:
        mod_Tem = 30.9
    else: 
        mod_Tem = mod_temp
    
    random_df1 = pd.DataFrame(random_dict,
                         index = [['0']],
                         columns = ["field1", "field2", "field3"])
    
    random_df = random_df1.values
    
    #We need to get rid of the missing values before training:
    np.nan_to_num(random_df[:,0:1], copy=False, nan=24.9) #this is field1
    np.nan_to_num(random_df[:,1:2], copy=False, nan=39.4) #this is field2
    np.nan_to_num(random_df[:,2:3], copy=False, nan=30.9) #this is field3
    
    prediction = tf.keras.models.load_model("model2.pkl").predict(random_df)
    
    prediction=round(abs(prediction[0][0]), 3)
    #calculation for the error:
    per_error = ((prediction - power)/power)*100
    #the explanation messages
    #include the sign of the error in the explanation, is it and under or over estimation?
    return render_template("predict.html",field11 = air_temp, field22 = rel_hum, field33 =  mod_temp , field44 = Dust, 
                           field55 = atm_pres, field66 = CO_gas, Actual = power, Predicted = prediction, 
                           Error=round(abs(per_error),2))

if __name__=='__main__':
    app.run(debug=False)
