# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 17:11:55 2015

Reads Hearthstone card data in as a JSON file and saves it to a CSV

@author: Jacob
"""

#import pandas as pd
import json as js
import urllib.request as urllib

URL = "https://api.hearthstonejson.com/v1/13921/enUS/cards.collectible.json"
OUT_FILE = "collectibles.json"
        
              
request = urllib.Request(URL, None, headers={'User-Agent':'Mozilla'})
response = urllib.urlopen(request)

data = js.loads(response.read().decode('utf-8'))

with open(OUT_FILE, 'w') as outfile:
    js.dump(data, outfile)









PROPERTIES = ['name',
              'artist',
              'collectible',
              'cost',
              'durability',
              'howToGet',
              'howToGetGold',
              'elite',
              'faction',
              'flavor',
              'health',
              'id',
              'inPlayText',
              'playerClass',
              'race',
              'rarity',
              'text',
              'type']