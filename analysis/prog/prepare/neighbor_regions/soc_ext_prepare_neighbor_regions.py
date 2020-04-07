#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:55:29 2020

@author: marcfabel

Descritpion:
    Generate overview: relates active AGS(regions with a stadium) to the ags 
    that are sorounding the active AGS
    
Inputs:
     - map_stadiums_AGS_neighbours.csv      [intermed_maps]  comes as output from QGIS, raw - key variable: NEIGHBORS

Outputs:
     - neighbor_regions_prepared.csv       [intermed_maps]   which active ags has which sorounding regions
                                                             -> used in QGIS again to select neighbor regions


"""


import pandas as pd
import numpy as np

z_maps_input_intermediate =   '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'
z_maps_output_intermediate =  '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'


# read in data
data = pd.read_csv(z_maps_input_intermediate + 'map_stadiums_AGS_neighbours.csv', sep=';')
data.sort_values(by=['AGS'], inplace=True)
data.reset_index(inplace=True, drop=True)

neighbors = data['NEIGHBORS'].str.split(',', expand=True)


# edit neighbors (drop regions that are actually active themselves
# thus they cannot serve as neighbor region
neighbors = neighbors.replace('01002000', np.nan)                               # delete Kiel
neighbors = neighbors.replace('03', np.nan)                                     # error in data for Hamburg 
neighbors = neighbors.replace('04011000', np.nan)                               # delete Bremen
neighbors = neighbors.replace('04012000', np.nan)                               # delete Bremerhaven
neighbors = neighbors.replace('05315000', np.nan)                               # delete Koeln
neighbors = neighbors.replace('05316000', np.nan)                               # delete Leverkusen
neighbors = neighbors.replace('05111000', np.nan)                               # delete Dusseldorf
neighbors = neighbors.replace('05112000', np.nan)                               # delete Duisburg
neighbors = neighbors.replace('05119000', np.nan)                               # delete Oberhausen
neighbors = neighbors.replace('05513000', np.nan)                               # delete Gelsenkirchen
neighbors = neighbors.replace('05911000', np.nan)                               # delete Bochum
neighbors = neighbors.replace('05913000', np.nan)                               # delete Dortmund
neighbors = neighbors.replace('06412000', np.nan)                               # delete Frankfurt
neighbors = neighbors.replace('06413000', np.nan)                               # delete Offenbach
neighbors = neighbors.replace('06414000', np.nan)                               # delete Wiesbaden
neighbors = neighbors.replace('07315000', np.nan)                               # delete Mainz
neighbors = neighbors.replace('08135019', np.nan)                               # delete Heidenheim
neighbors = neighbors.replace('08136088', np.nan)                               # delete Aalen
neighbors = neighbors.replace('09162000', np.nan)                               # delete Munich
neighbors = neighbors.replace('09184148', np.nan)                               # delete Unterhaching
neighbors = neighbors.replace('09563000', np.nan)                               # delete Fürth
neighbors = neighbors.replace('09564000', np.nan)                               # delete Nürnberg
neighbors = neighbors.replace('11000000', np.nan)                               # delete Berlin
neighbors = neighbors.replace('12054000', np.nan)                               # delete Potsdam
neighbors = neighbors.replace('13003000', np.nan)                               # delete Rostock

neighbors.fillna(value=pd.np.nan, inplace=True)
data = pd.concat([data[['AGS', 'stadium']], neighbors], axis=1) # 'GEN', 'DES'


# bring data set in the right format
data = pd.melt(data, id_vars=['AGS','stadium'], var_name='neighbor', 
               value_name='neighbor_ags')

# sort data according to AGS
data.sort_values(by=['AGS', 'neighbor_ags'], inplace=True)
data.reset_index(inplace=True, drop=True)

# drop nans
data = data.dropna()

#rename columns
data.rename(columns={'AGS':'neighbor_to_ags', 'stadium':'neighbor_to_stadium',
                     'neighbor_ags':'AGS'}, inplace=True)

data.drop(['neighbor'], inplace=True, axis=1)

data.to_csv(z_maps_output_intermediate + 'neighbor_regions_prepared.csv', sep=';', encoding='UTF-8', index=False)


###############################################################################
#           END OF FILE
###############################################################################