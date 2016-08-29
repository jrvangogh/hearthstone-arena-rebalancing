# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 22:09:08 2016

@author: Jacob van Gogh
"""

import numpy as np
import random
from bisect import bisect
import statistics as stat
from scipy.stats import norm
import pandas as pd
import warnings

class ArenaDraftSimulator:
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
        self.draft = None


    def offer_card(self):
        """
        Randomly selects a card using card weights and returns
        its name and score in a tuple
        """
        r = random.random() * self.total_weight
        i = bisect(self.cum_weights, r)
        return( (self.scores[i], self.names[i]) )


    def offer_cards(self, num_iter):
        """
        Randomly selects multiple cards
        """
        return ([self.offerCard() for c in range(num_iter)])


    def draft_card(self, max_only=True):
        """
        Randomly selects 3 cards and returns the one
        with the highest arena score
        """
        return max([self.offerCards(3)])


    def draft_cards(self, num_iter, as_DF=False):
        """
        Randomly drafts multiple cards and stores this draft
        for stats
        """
        self.draft = [self.draftCard() for c in range(num_iter)]
        return self.getDraft(as_DF)

    
    def get_draft(self, as_DF=False):
        """
        Returns the draft of cards
        """
        if as_DF:
            return pd.DataFrame(self.draft, columns=['score','name'])
        return self.draft


    def get_draft_stats(self):
        """
        Returns a stastical description of the scores of the draft
        """
        return (self.getDraft(as_DF=True)['score'].describe())


#%% Methods for Calculating Weights of a Standard Arena Draft

CLASSES = ['DRUID', 'HUNTER', 'MAGE', 'PALADIN', 'PRIEST', 
           'ROGUE', 'SHAMAN', 'WARLOCK', 'WARRIOR']
RARITY_RATES = {'COMMON': 76, 'RARE': 20, 'EPIC': 3, 'LEGENDARY': 1}


def add_standard_weight(df, col_name='weight'):
    """
    Given a data frame of arena cards, adds a column that
    contains the probabilities of each card being offered
    Necessary columns:
    arenaScoreClass - value of each class arena set
        * values - each class in all caps
    playerClass - value of the card's class set
        * values - each class and 'neutral' in all caps
    rarity - rarity of each card
        * values - 'common', 'rare', 'epic', 'legendary' in all caps
    """
    # Silence warnings due to pandas bug
    warnings.simplefilter(action = "ignore", category = RuntimeWarning)
    
    # For every class
    for c in CLASSES:
        # For every rarity
        for r in RARITY_RATES:
            # Slice the data frame for a particular arena set and rarity
            if r == 'COMMON':
                f = df[(df['arenaScoreClass'] == c) & \
                       ((df['rarity'] == r) | (df['rarity'] == 'FREE'))]
            else:
                f = df[(df['arenaScoreClass'] == c) & (df['rarity'] == r)]
            
            # Count the number of cards based on rarities and class
            full_count = len(f)
            class_count = len(f[f['playerClass'] == c])
            neutral_count = full_count - class_count
            
            # Calculate the weight of the cards
            eff_count = full_count + class_count
            neut_w = RARITY_RATES[r] / eff_count
            class_w = 2 * neut_w
            print(c, r)
            print(full_count, class_count, neutral_count)
            print(class_w, neut_w)
            print(class_count * class_w, neutral_count * neut_w, class_count * class_w + neutral_count * neut_w)
            print('')
            
            # Set the cards' weights
            if r == 'COMMON':
                df.set_value((df['arenaScoreClass'] == c) & \
                             (df['playerClass'] == c) & \
                             ((df['rarity'] == r) | (df['rarity'] == 'FREE')),
                             col_name, class_w)
                         
                df.set_value((df['arenaScoreClass'] == c)& \
                             (df['playerClass'] == 'NEUTRAL') & \
                             ((df['rarity'] == r) | (df['rarity'] == 'FREE')),
                             col_name, neut_w)
            else:
                df.set_value((df['arenaScoreClass'] == c) & \
                             (df['playerClass'] == c) & \
                             (df['rarity'] == r),
                             col_name, class_w)
                         
                df.set_value((df['arenaScoreClass'] == c)& \
                             (df['playerClass'] == 'NEUTRAL') & \
                             (df['rarity'] == r),
                             col_name, neut_w)
    return df


def add_linear_weight(df, scale=1, buffer=0, col_name='weightLinear'):
    """
    Given a data frame of arena cards, adds a column that
    calculates the weight of a card being offered as a
    linear correlation to its arena score
    """
    df[col_name] = scale * df['arenaScore'] + buffer
    df[col_name] = df[col_name] / sum(df[col_name])
    return df


def add_inverse_weight(df, scale=1, buffer=0, col_name='weightInverse'):
    """
    Given a data frame of arena cards, adds a column that
    calculates the weight of a card being offered as an
    inverse correlation to its arena score
    """
    df[col_name] = scale / df['arenaScore'] + buffer
    df[col_name] = df[col_name] / sum(df[col_name])
    return df


def add_linear_centered_weight(df, center_val=None, max_val=None,
                               col_name='weightLinearCenter'):
    """
    Given a data frame of arena cards, adds a column that
    calculates the weight of a card based on its arena score.
    The weight scales linearly based on the difference 
    between a card's arena score and the center value score.
    """
    if center_val is None:
        center_val = stat.median(df['arenaScore'])
    if max_val is None:
        max_val = max( max(df['arenaScore']) - center_val, 
                       center_val - min(df['arenaScore']) )
    
    df[col_name] = max_val - abs(df['arenaScore'] - center_val)
    num = df._get_numeric_data()
    num[num < 0] = 0
    df[col_name] = df[col_name] / sum(df[col_name])
    return df


def add_normal_weight(df, mean=None, variance=0.5,
                      col_name='weightNormal'):
    """
    Given a data frame of arena cards, adds a column that
    calculates the weight of a card based on its arena score.
    The weight is calculated using a normal distributions
    PDF on arena scores.
    """
    if mean is None:
        mean = stat.median(df['arenaScore'])
    n = norm(loc=mean, scale=variance)
    df[col_name] = n.pdf(df['arenaScore'])
    return df


def add_all_weights(df, center_val=None, arg_dict=None):
    """
    Given a data frame, adds all of the above weight
    columns using the parameters contained in the
    arg_dict. The keys of the arg_dict refer to the
    names of each weight calculation:
    'linear', 'inverse', 'linear_center', 'normal'
    If a dictionary is not passed, you can simply pass
    in a data frame (and potentially a center value).
    """
    if arg_dict is None:
        add_linear_weight(df)
        add_inverse_weight(df)
        add_linear_centered_weight(df, center_val=center_val)
        add_normal_weight(df, mean=center_val)
    else:
        add_linear_weight(**arg_dict['linear'])
        add_inverse_weight(**arg_dict['inverse'])
        add_linear_centered_weight(**arg_dict['linear_center'])
        add_normal_weight(**arg_dict['normal'])


def INCORRECT_add_standard_weight(df):
    """
    ----THIS FUNCTION IS CURRENTLY THOUGHT TO BE INCORRECT----
    Given a data frame of arena cards, adds a column that
    contains the probabilities of each card being offered
    Necessary columns:
    arenaScoreClass - value of each class arena set
        * values - each class in all caps
    playerClass - value of the card's class set
        * values - each class and 'neutral' in all caps
    rarity - rarity of each card
        * values - 'common', 'rare', 'epic', 'legendary' in all caps
    """
    CLASS_RATES = {True: (2/3), False: (1/3)}
    # Silence warnings due to pandas bug
    warnings.simplefilter(action = "ignore", category = RuntimeWarning)
    
    # For every class
    for c in CLASSES:
        # For every rarity
        for r in RARITY_RATES:
            # Slice the data frame for a particular arena set and rarity
            if r == 'COMMON':
                f = df[(df['arenaScoreClass'] == c) & \
                       ((df['rarity'] == r) | (df['rarity'] == 'FREE'))]
            else:
                f = df[(df['arenaScoreClass'] == c) & (df['rarity'] == r)]
            
            # Count the number of cards based on rarities and class
            full_count = len(f)
            class_count = len(f[f['playerClass'] == c])
            neutral_count = full_count - class_count
            
            # Calculate the weight of the cards
            class_w = RARITY_RATES[r] * CLASS_RATES[True] / class_count
            neut_w = RARITY_RATES[r] * CLASS_RATES[False] / neutral_count
            
            # Set the cards' weights
            if r == 'COMMON':
                df.set_value((df['arenaScoreClass'] == c) & \
                             (df['playerClass'] == c) & \
                             ((df['rarity'] == r) | (df['rarity'] == 'FREE')),
                             'weight', class_w)
                         
                df.set_value((df['arenaScoreClass'] == c)& \
                             (df['playerClass'] == 'NEUTRAL') & \
                             ((df['rarity'] == r) | (df['rarity'] == 'FREE')),
                             'weight', neut_w)
            else:
                df.set_value((df['arenaScoreClass'] == c) & \
                             (df['playerClass'] == c) & \
                             (df['rarity'] == r),
                             'weight', class_w)
                         
                df.set_value((df['arenaScoreClass'] == c)& \
                             (df['playerClass'] == 'NEUTRAL') & \
                             (df['rarity'] == r),
                             'weight', neut_w)
    return df