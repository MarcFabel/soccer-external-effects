# -*- coding: utf-8 -*-
"""
Created on Tue Apr 7 2020

@author: marcfabel


Descritpion:
     This file combines all the prepared data files in a wide format on the AGS-day level


Inputs:
     - Schulferien_1015.dta                         final          panel(bula,day)_ indicating vacations, holidays, and special days (! has to be transferred manually from F to dropbox)
     - soccer_prepared.csv                          final          on the match level, output of prepare_soccer_data.py
     - weather_prepared.csv                         final          panel(ags,day) with weather variables
     - crime_neighbor_regions_prepared.csv          final          panel(ags,day) with number of assaults
     - regional_data_neighbor_regions_prepared.csv  final          panel(ags,year)
     - neighbor_regions_prepared.csv                intermed_maps  comes as output from QGIS, which regions are neighbours to AGS which contain a stadium


Outputs:
     - data_prepared_neighbor_regions.csv            final          merged df


"""

# packages
from datetime import datetime
import pandas as pd
import numpy as np
import time
start_time = time.time()


# paths (work LOCAL)
#z_prepared_data =             'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'
#z_maps_input_intermediate =   'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'
#z_data_output_Dx =            'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'
#z_data_output =               'F:/econ/soc_ext/analysis/data/final/'
#z_prefix =                    'soc_ext_'


# paths HOME
z_prepared_data =             '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_maps_input_intermediate =   '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'
z_data_output_Dx =            '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_prefix =                    'soc_ext_'
#z_data_output =              not applicable


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
double_matches['d_multi_games'] = 1
# drop smaller game league = 3 ( affects 6 games: Stuttgarter Kickers 2x, VfB 3x, and Fortuna Köln)
soccer = soccer.merge(double_matches, on=['date', 'home_team'], how='outer')
soccer['d_multi_games'].fillna(0, inplace=True)
soccer.drop( soccer[ (soccer['d_multi_games'] == 1) & (soccer['league'] == 3)].index, inplace=True)
soccer['d_gameday'] = 1

soccer.rename(columns={'AGS':'neighbor_to_ags'},inplace=True)

# keep only small set of variables (ONLY HERE FOR NEIGHBORS)
soccer = soccer[['season', 'date', 'neighbor_to_ags', 'd_gameday']]




########## WEATHER ##########
weather = pd.read_csv(z_prepared_data + 'weather_prepared.csv', sep=';', encoding='UTF-8')
# cut weather to the right time window
weather['date'] = pd.to_datetime(weather['date'], format='%Y-%m-%d')
weather.drop( weather[  (weather.date < start) | (weather.date > end)].index, inplace=True)
weather.drop(['Unnamed: 0'], inplace=True, axis=1)

# add information to which districts the AGS are neighboring
neighbor_regions = pd.read_csv(z_maps_input_intermediate + 'neighbor_regions_prepared.csv',
                               sep=';', encoding='UTF-8')
neighbor_regions.drop('neighbor_to_stadium', inplace=True, axis=1)
neighbor_regions.drop_duplicates(inplace=True)
weather.rename(columns={'AGS':'neighbor_to_ags'},inplace=True)
weather = weather.merge(neighbor_regions, on='neighbor_to_ags', how='outer')




########## CRIME ##########
assaults = pd.read_csv(z_prepared_data + 'crime_neighbor_regions_prepared.csv', sep=';', encoding='UTF-8') # when updated: has to be copied from F!
assaults.drop(['bula'], inplace=True, axis=1)
assaults.rename(columns={'date_d_mod':'date', 'location':'AGS'}, inplace=True)
assaults['date'] = pd.to_datetime(assaults['date'], format='%Y-%m-%d')




########## REGIONAL DATA BASE ##########
regional_data = pd.read_csv(z_prepared_data + 'regional_data_neighbor_regions_prepared.csv', sep=';', encoding='UTF-8')




###############################################################################
#       2) Combine all data frames
###############################################################################

# generate data frame with 1,059,090 TxR rows (T=365+366+365+365+181=1642)  X  (R=645)
data = weather.copy()
data['bula'] = data.neighbor_to_ags.apply(lambda x: x/1000000).astype(int)
# generate other variables from the date variable
data['day'] 	= data.date.apply(lambda x: x.strftime('%d')).astype(int)
data['month'] 	= data.date.apply(lambda x: x.strftime('%m')).astype(int)
data['year'] 	= data.date.apply(lambda x: x.strftime('%Y')).astype(int)
data['dow'] 	= data.date.apply(lambda x: x.strftime('%a'))
data['doy'] 	= data.date.apply(lambda x: x.strftime('%j')).astype(int)
data['woy'] 	= data.date.apply(lambda x: x.strftime('%W')).astype(int)

data['days_in_year'] = np.where(data.year == 2012, 366, 365)


# merge Holidays
data = data.merge(holidays, on=['bula', 'date'], how='outer')


# merge Crime Data
data = data.merge(assaults, on=['date', 'AGS'], how='left')
assaults_cols = assaults.columns.drop(['date', 'AGS']).tolist() # to fill nr assaults with zeros for NaNs
data[assaults_cols] = data[assaults_cols].fillna(value=0)


# merge Regional Data Base
data = data.merge(regional_data, on=['AGS', 'year'], how='outer')


# merge Soccer data
data = data.merge(soccer, on=['neighbor_to_ags', 'date'], how='outer')
z_gameday_columns = ['d_gameday'] # gameday columns and interactions with gd
data[z_gameday_columns] = data[z_gameday_columns].fillna(0)






###############################################################################
#       Generate variables
###############################################################################

# generate assault rate
data['assrate']                 = (data['ass']                   * 100000 * data['days_in_year'])/data['pop_t']

# assault rates per gender and age-group
data['assrate_f']               = (data['ass_f']                 * 100000 * data['days_in_year'])/data['pop_t']
data['assrate_m']               = (data['ass_m']                 * 100000 * data['days_in_year'])/data['pop_t']




########## FILL IN SEASON FOR NON GAME DAYS ###################################
# july - may is season
data['season2'] = np.nan

for year in range(z_first_year_wave-1, z_last_year_wave):
     start_season = datetime(year,7,1)
     end_season = datetime(year+1,5,31)

     year_identifier = (data.date >= start_season) & (data.date <= end_season)
     data.loc[year_identifier, 'season2'] = str(year) + '-' + str(year+1)[-2:]
data.drop('season', inplace=True, axis=1)
data.rename(columns={'season2':'season'}, inplace=True)


# drop junes
data.drop(data[data.month==6].index, inplace=True)




###############################################################################
#       Read out
###############################################################################
#data.to_csv(z_data_output + 'data_prepared.csv', sep=';', encoding='UTF-8', index=False)
data.to_csv(z_data_output_Dx + 'data_prepared_neighbor_regions.csv', sep=';', encoding='UTF-8', index=False)



###############################################################################
#       END OF FILE
###############################################################################
print("--- %s seconds ---" % (time.time() - start_time))




