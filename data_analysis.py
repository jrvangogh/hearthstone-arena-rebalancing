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

iterations = 3000000
score_median = stat.median(data[data['arenaScoreClass'] == 'SHAMAN']['arenaScore'])

#%% Add New Columns for Different Weight Formulas
hak.add_all_weights(df=data, center_val=score_median)
data.to_csv(DATA_CSV, index=False)


#%% Gather Draft Data for Different Weight Formulas
stats = []
for c in hak.CLASSES:
    f = data[data['arenaScoreClass'] == c]
    for formula, col_name in hak.DEFAULT_WEIGHT_FORMULAS.items():
        cols = [col_name, 'name', 'arenaScore']
        ads = hak.ArenaDraftSimulator(card_df=f, df_cols=cols)
        ads.draft_cards(num_iter=iterations)
        stat = ads.get_draft_stats()
        stat['class'] = c
        stat['formula'] = formula
        stats.append(stat.transpose())
stats = pd.concat(stats, axis=1).transpose()
stats = stats.sort(columns=['formula', 'class'])
stats = stats.reset_index()
cols = ['formula', 'class', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
stats = stats[cols]
stats.to_csv(STATS_CSV, index=False)