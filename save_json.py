# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 17:11:55 2015

Reads Hearthstone card data in as a JSON file and saves it to a CSV

@author: Jacob
"""

#%% Import and Set Constants
import json as js
import urllib.request as urllib
import pandas as pd
import requests
from lxml import html

CARD_DATA_URL = "https://api.hearthstonejson.com/v1/13921/enUS/cards.collectible.json"
CARD_ARENA_SCORES_URL = "http://www.heartharena.com/tierlist"
JSON_OUT_FILE = "collectibles.json"
CSV_OUT_FILE = "collectibles.csv"
ARENA_OUT_FILE = "arena_data.csv"
ARENA_COLS = ['id',
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

CLASSES = ['druid', 'hunter', 'mage', 'paladin', 'priest', 
           'rogue', 'shaman', 'warlock', 'warrior', 'any']
        
#%% Get Card Data As JSON File
request = urllib.Request(CARD_DATA_URL, None, headers={'User-Agent':'Mozilla'})
response = urllib.urlopen(request)

data_json = js.loads(response.read().decode('utf-8'))

with open(JSON_OUT_FILE, 'w') as outfile:
    js.dump(data_json, outfile)

data_dataframe = pd.read_json(JSON_OUT_FILE)
data_dataframe.to_csv(CSV_OUT_FILE)

arena_dataframe = data_dataframe[data_dataframe['type'] != 'HERO']
arena_dataframe = arena_dataframe[ARENA_COLS]
arena_dataframe.to_csv(ARENA_OUT_FILE)


#%% Get Card Arena Scores From HearthArena

page = requests.get(CARD_ARENA_SCORES_URL)
tree = html.fromstring(page.content)

score_dict = {c:{} for c in CLASSES}
for hs_class in CLASSES:
    d = score_dict[hs_class]
    xpath_string = '//section[@id="' + hs_class + '"]'
    section = tree.xpath(xpath_string)[0]
    
    for rarity in section.xpath('ul/li'):
        for tier in rarity.xpath('ul/li'):
            for card in tier.xpath('ol/li'):
                name = card.xpath('dl/dt')[0].text.strip()
                if name:
                    score = int(card.xpath('dl/dd')[0].text)
                    d[name] = score


#%% Separate Arena Data By Class
df_dict = {c:{} for c in CLASSES}
neutral = arena_dataframe[arena_dataframe['playerClass'] == 'NEUTRAL']
for hs_class in CLASSES:
    class_df = arena_dataframe[arena_dataframe['playerClass'] == hs_class.upper()]
    class_df = class_df.append(neutral)
    class_df['arenaScoreClass'] = hs_class.upper()
    df_dict[hs_class] = class_df
    
