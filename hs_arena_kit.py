# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 22:09:08 2016

@author: Jacob van Gogh
"""

import numpy as np
import random
from bisect import bisect

class ArenaDraftCalculator:
    def __init__(self, card_weights=None, card_names=None, card_scores=None,
                 card_tuples=None, card_df=None, df_cols=None):
        """
        Initializes the arena draft calculator. This can be done in one of 
        three ways:
        1)
        card_weights: list of probabilities of being offered each card
        card_names: list of names of each card
        card_scores: list of arena scores for each card
        2)
        card_tuples: list of tuples containing the top 3 properties of each card
        3)
        card_df: a data frame containing the 3 properties
        df_cols: list of column names containing these properties
        
        """
        if card_tuples is None and card_df is None:
            self.weights = card_weights
            self.names = card_names
            self.scores = card_scores
            
        elif card_tuples is None:
            self.weights = list(card_df[df_cols[0]])
            self.names = list(card_df[df_cols[1]])
            self.scores = list(card_df[df_cols[2]])
            
        else:
            self.weights = [c[0] for c in card_tuples]
            self.names = [c[1] for c in card_tuples]
            self.scores = [c[2] for c in card_tuples]
        
        self.cum_weights = list(np.cumsum(self.weights))
        self.total_weight = self.cum_weights[-1]


    def offerCard(self):
        """
        Randomly selects a card using card weights and returns
        its name and score in a tuple
        """
        r = random.random() * self.total_weight
        i = bisect(self.cum_weights, r)
        return( (self.names[i], self.scores[i]) )