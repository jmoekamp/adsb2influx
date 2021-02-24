#!/usr/bin/python3

import json
import requests
from influxdb import InfluxDBClient 
import sys
import great_circle_calculator.great_circle_calculator as gcc

# Please configure according to your site

ip = ""
influxdbserver= ""
influxdbusername= ""
influxdbpassword = ""
influxdbdbname = "" 

url_receiver = "http://"+ ip +":8080/data/receiver.json"
result_receiver = requests.get(url_receiver).text
data_receiver = json.loads(result_receiver) 
lat_receiver=data_receiver["lat"]
lon_receiver=data_receiver["lon"]

url = "http://"+ ip +":8080/data/aircraft.json"
result = requests.get(url).text
data = json.loads(result) 
max_distance=0
max_bearing=0

aircrafts=data["aircraft"]
for aircraft in aircrafts:
    lon = aircraft.get("lon")
    lat = aircraft.get("lat")
    flight = aircraft.get("flight")
    if (lat):
        p1, p2 = (lon_receiver, lat_receiver), (lon, lat)
        distance = gcc.distance_between_points(p1, p2, unit='meters', haversine=True)
        bearing = gcc.bearing_at_p1(p1, p2)
        if distance > max_distance:
            max_bearing=bearing
            max_distance=distance

url_stats = "http://"+ ip +":8080/data/stats.json"

result_stats = requests.get(url_stats).text
data_stats = json.loads(result_stats) 
data_stats_local = data_stats["last1min"]["local"]

client = InfluxDBClient(influxdbserver,8086, influxdbusername , influxdbpassword, influxdbdbname)
json_body = [
		{
            "measurement": "adsb",
            "tags": {
                "host": ip
            },
            "fields": {
                "messages": data_stats["last1min"]["messages"],
                "maxdistance": max_distance,
                "maxbearing": max_bearing,
                "noise": data_stats_local["noise"],
                "signal": data_stats_local["signal"],
                "strong_signals": data_stats_local["strong_signals"],
                "bad": data_stats_local["bad"],
                "peak_signal": data_stats_local["peak_signal"]
            }
        }
    ]

client.write_points(json_body)


