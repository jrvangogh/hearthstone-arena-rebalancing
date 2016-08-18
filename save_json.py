# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 17:11:55 2015

Reads Hearthstone card data in as a JSON file and saves it to a CSV

@author: Jacob
"""

#import pandas as pd
import json as js
import urllib.request as urllib
import pandas as pd

URL = "https://api.hearthstonejson.com/v1/13921/enUS/cards.collectible.json"
JSON_OUT_FILE = "collectibles.json"
CSV_OUT_FILE = "collectibles.csv"
ARENA_OUT_FILE = "arena_data.csv"
arena_cols = ['id',
              'set',
              'name', 
              'rarity', 
              'playerClass',
              'type', 
              'cost',
              'attack',
              'health',
              'durability',
              'mechanics',
              'overload']
        
              
request = urllib.Request(URL, None, headers={'User-Agent':'Mozilla'})
response = urllib.urlopen(request)

data_json = js.loads(response.read().decode('utf-8'))

with open(JSON_OUT_FILE, 'w') as outfile:
    js.dump(data_json, outfile)

data_dataframe = pd.read_json(JSON_OUT_FILE)
data_dataframe.to_csv(CSV_OUT_FILE)

arena_dataframe = data_dataframe[data_dataframe['type'] != 'HERO']
arena_dataframe = arena_dataframe[arena_cols]
arena_dataframe.to_csv(ARENA_OUT_FILE)