# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 15:19:40 2016

@author: Jacob van Gogh
"""

import pandas as pd
import statistics as stat
import hs_arena_kit as hak

DATA_CSV = "arena_data.csv"
STATS_CSV = "stats.csv"

data = pd.read_csv("arena_data.csv")
classes = list(data["arenaScoreClass"].unique())

iterations = 10
score_median = stat.median(data[data['arenaScoreClass'] == 'SHAMAN']['arenaScore'])

#%% Add New Columns for Different Weight Formulas
hak.add_all_weights(df=data, center_val=score_median)