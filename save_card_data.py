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

#%% "Fix" Current Pandas Bug with NaN Values and Large Dataframes
import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)
        
#%% Get Card Data As JSON File
request = urllib.Request(CARD_DATA_URL, None, headers={'User-Agent':'Mozilla'})
response = urllib.urlopen(request)

data_json = js.loads(response.read().decode('utf-8'))

with open(JSON_OUT_FILE, 'w') as outfile:
    js.dump(data_json, outfile)

data_df = pd.read_json(JSON_OUT_FILE)

arena_df = data_df[data_df['type'] != 'HERO']
arena_df = arena_df[ARENA_COLS]


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
neutral_df = arena_df[arena_df['playerClass'] == 'NEUTRAL']
for hs_class in CLASSES:
    if hs_class != 'any':
        class_df = arena_df[arena_df['playerClass'] == hs_class.upper()]
        class_df = class_df.append(neutral_df.copy())
        class_df['arenaScoreClass'] = hs_class.upper()
    else:
        class_df = neutral_df.copy()
        class_df['arenaScoreClass'] = 'NEUTRAL'
    df_dict[hs_class] = class_df
    

#%% Add Arena Scores
def get_score(card_name, score_dict):
    return score_dict.get(card_name)

for hs_class in CLASSES:
    d = score_dict[hs_class]
    df = df_dict[hs_class]
    df['arenaScore'] = df['name'].apply(get_score, args=(d,))


#%% Combine Together In One Data Frame And Remove Cards With No Arena Score
arena_df = pd.concat([df_dict[df] for df in df_dict])
arena_df = arena_df[arena_df.arenaScore.notnull()]
arena_df.to_csv(ARENA_OUT_FILE, index=False)