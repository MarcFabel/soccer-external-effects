# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 16:36:35 2019

@author: fabel


Descritpion:
     This file combines all the prepared data files in a wide format on the AGS-day level


Inputs:
     - Schulferien_1015.dta                  final          panel(bula,day)_ indicating vacations, holidays, and special days (! has to be transferred manually from F to dropbox)
     - soccer_prepared.csv                   final          on the match level, output of prepare_soccer_data.py
     - weather_prepared.csv                  final          panel(ags,day) with weather variables
     - crime_prepared.csv                    final          panel(ags,day) with number of assaults
     - regional_data_prepared.csv            final          panel(ags,year)
     - map_stadiums_AGS.csv                  intermed_maps  comes as output from QGIS, which AGS contain a stadium


Outputs:


"""

# packages
from datetime import datetime
import pandas as pd
import numpy as np
import time
start_time = time.time()


# paths
z_prepared_data =             'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_maps_input_intermediate =   'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'
z_prefix =                    'soc_ext_'



# magic numbers
z_first_year_wave = 2011
z_last_year_wave = 2015

###############################################################################
#       1) Read in data frames
###############################################################################



########## HOLIDAYS ##########
holidays = pd.read_stata(z_prepared_data + 'Schulferien_1015.dta')         # when updated: has to be copied from F!
holidays[['bula', 'sch_hday', 'pub_hday', 'fasching']] = holidays[['bula', 'sch_hday', 'pub_hday', 'fasching']].astype(int)
start = datetime(z_first_year_wave,1,1)
end = datetime(z_last_year_wave,6,30)
holidays.drop( holidays[  (holidays.mdy < start) | (holidays.mdy > end)].index, inplace=True)
holidays['day'] = holidays.mdy.apply(lambda x: x.strftime('%d'))
holidays['month'] = holidays.mdy.apply(lambda x: x.strftime('%m'))
holidays['silvester'] = np.where( (holidays.day == '31') & (holidays.month == '12'), 1, 0)
holidays['special_day'] = np.where( (holidays.fasching == 1) | (holidays.silvester == 1), 1, 0)
holidays.drop(['day','month', 'fasching', 'silvester'], inplace=True, axis=1)
holidays.rename(columns={'mdy':'date'}, inplace=True)



########## SOCCER ##########
soccer = pd.read_csv(z_prepared_data + 'soccer_prepared.csv', sep=';', encoding='UTF-8')
# map: stadium -> AGS
stadiums_regions = pd.read_csv(z_maps_input_intermediate + 'map_stadiums_AGS.csv', sep=';')
stadiums_regions = stadiums_regions[['stadium', 'AGS']]
soccer = soccer.merge(stadiums_regions, on='stadium', how='left')
soccer['date'] = pd.to_datetime(soccer['date'], format='%Y-%m-%d')
# cut soccer to the right time window
soccer.drop( soccer[  (soccer.date < start) | (soccer.date > end)].index, inplace=True)
# two matches in same AGS on the same day
double_matches = soccer[soccer.duplicated(subset=['date', 'AGS'], keep = False)]
double_matches = double_matches[['date', 'home_team']]
double_matches['D_multi_games'] = 1
# drop smaller game league = 3 ( affects 6 games: Stuttgarter Kickers 2x, VfB 3x, and Fortuna Köln)
soccer = soccer.merge(double_matches, on=['date', 'home_team'], how='outer')
soccer['D_multi_games'].fillna(0, inplace=True)
soccer.drop( soccer[ (soccer['D_multi_games'] == 1) & (soccer['league'] == 3)].index, inplace=True)
soccer['D_gameday'] = 1


########## WEATHER ##########
weather = pd.read_csv(z_prepared_data + 'weather_prepared.csv', sep=';', encoding='UTF-8')
# cut weather to the right time window
weather['date'] = pd.to_datetime(weather['date'], format='%Y-%m-%d')
weather.drop( weather[  (weather.date < start) | (weather.date > end)].index, inplace=True)
weather.drop(['Unnamed: 0'], inplace=True, axis=1)



########## CRIME ##########
assaults = pd.read_csv(z_prepared_data + 'crime_prepared.csv', sep=';', encoding='UTF-8') # when updated: has to be copied from F!
assaults.drop(['bula'], inplace=True, axis=1)
assaults.rename(columns={'date_d_mod':'date', 'location':'AGS'}, inplace=True)
assaults['date'] = pd.to_datetime(assaults['date'], format='%Y-%m-%d')



########## REGIONAL DATA BASE ##########
regional_data = pd.read_csv(z_prepared_data + 'regional_data_prepared.csv', sep=';', encoding='UTF-8')




###############################################################################
#       2) Combine all data frames
###############################################################################


# generate data frame with 96878 TxR rows (T=365+366+365+365+181=1642)  X  (R=59)
data = weather.copy()
data['bula'] = data.AGS.apply(lambda x: x/1000000).astype(int)
# generate other variables from the date variable
data['day'] 	= data.date.apply(lambda x: x.strftime('%d')).astype(int)
data['month'] 	= data.date.apply(lambda x: x.strftime('%m')).astype(int)
data['year'] 	= data.date.apply(lambda x: x.strftime('%Y')).astype(int)
data['dow'] 	= data.date.apply(lambda x: x.strftime('%a'))
data['doy'] 	= data.date.apply(lambda x: x.strftime('%j')).astype(int)
data['woy'] 	= data.date.apply(lambda x: x.strftime('%W')).astype(int)

data['days_in_year'] = np.where(data.year == 2012, 366, 365)




# merge other data frames to it
data = data.merge(holidays, on=['bula', 'date'], how='outer')
data = data.merge(assaults, on=['date', 'AGS'], how='outer')
data.offences.fillna(0, inplace=True)
data = data.merge(regional_data, on=['AGS', 'year'])

# merge soccer
data = data.merge(soccer, on=['AGS', 'date'], how='outer')
# result should be 96878 x 296












###############################################################################
#       Generate variables
###############################################################################

# generate assault rates
data['assault_rate'] = (data['offences'] * 100000 * data['days_in_year'])/data['pop_t']








###############################################################################
#       END OF FILE
###############################################################################
print("--- %s seconds ---" % (time.time() - start_time))

# XXX TO DO:
# regional_data: finish with generating the variables from other columns and drop irrelevnt ones, as they serve as input elsewhere
# for a later time: kick weird stadiums out
# ACTIVE REGIONS ARE NOT ACTIVE ALL THE TIME, IN SOME YEARS SOME TEAMS ARE NOT EVEN PART OF THE THIRD LEAGUE



