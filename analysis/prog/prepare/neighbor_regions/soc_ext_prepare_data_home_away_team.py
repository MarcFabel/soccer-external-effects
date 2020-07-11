#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 17:53:25 2020

@author: marcfabel


Descritpion:
     This file combines all the prepared data files in a wide format on the AGS-day level


Inputs:
     - Schulferien_1015.dta                  final          panel(bula,day)_ indicating vacations, holidays, and special days (! has to be transferred manually from F to dropbox)
     - soccer_prepared_table_based.csv       intermed_soc   on the table level, output of prepare_soccer_data.py
     - weather_prepared.csv                  final          panel(ags,day) with weather variables
     - crime_prepared.csv                    final          panel(ags,day) with number of assaults
     - regional_data_prepared.csv            final          panel(ags,year)
     - map_stadiums_AGS.csv                  intermed_maps  comes as output from QGIS, which AGS contain a stadium


Outputs:
     - data_prepared                         final          merged df


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
z_soccer_input_intermediate   = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/soccer/'
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

#call the df soccer2 to emphasize distinction from match-based version in the normal program 
# besides, the df only contains league 1 & 2: - >to have clear treatment status of the region
soccer2 = pd.read_csv(z_soccer_input_intermediate + 'soccer_prepared_table_based.csv', sep=';', encoding='UTF-8')
soccer2 = soccer2[soccer2.league!=3]

# map: team -> AGS
team_stadium = soccer2[soccer2.D_home_game == 1][['team', 'stadium']].drop_duplicates()
stadiums_regions = pd.read_csv(z_maps_input_intermediate + 'map_stadiums_AGS.csv', sep=';')
stadiums_regions = stadiums_regions[['stadium', 'AGS']]
team_region = team_stadium.merge(stadiums_regions, on='stadium',how='left')
team_region.drop(team_region.stadium[team_region.stadium == 'Lohmühle, Lübeck'].index,inplace=True)
team_region = team_region[['team', 'AGS']].drop_duplicates()
soccer2 = soccer2.merge(team_region, on='team', how='left' )

# cut soccer to the right time window
soccer2['date'] = pd.to_datetime(soccer2['date'], format='%d.%m.%Y')
soccer2.drop( soccer2[  (soccer2.date < start) | (soccer2.date > end)].index, inplace=True)

# deal with two macthes in same ags at same day: first identify double matches - sort such that it keeps the home games if there are any, drop the relevant rows in original data set and replace by edited rows

# two matches in same AGS on the same day (except for 7 cases there is always one home and home away game) - so I keep the home game
double_matches = soccer2[soccer2.duplicated(subset=['date', 'AGS'], keep = False)].copy()
double_matches.sort_values(['date', 'AGS', 'D_home_game'], inplace=True)
double_matches.reset_index(inplace=True, drop=True)
double_matches.drop_duplicates(subset=['date', 'AGS'], keep='last', inplace=True)
# drop both duplicates from original data frame
soccer2.drop_duplicates(subset=['date', 'AGS'], keep = False, inplace=True)
# add the second of the dubplicates: mostly home games:
soccer2 = soccer2.append(double_matches)

# generate away game dummy
soccer2['D_away_game'] = np.where(soccer2.D_home_game == 0, 1, 0)






########## WEATHER ##########
weather = pd.read_csv(z_prepared_data + 'weather_prepared.csv', sep=';', encoding='UTF-8')
# cut weather to the right time window
weather['date'] = pd.to_datetime(weather['date'], format='%Y-%m-%d')
weather.drop( weather[  (weather.date < start) | (weather.date > end)].index, inplace=True)
weather.drop(['Unnamed: 0'], inplace=True, axis=1)

# keep only regions that are now in the sample:
regions_in_use = soccer2[['AGS']].drop_duplicates()
regions_in_use['region_used'] = 1
weather = weather.merge(regions_in_use, on='AGS')




########## CRIME ##########
assaults = pd.read_csv(z_prepared_data + 'crime_prepared.csv', sep=';', encoding='UTF-8') # when updated: has to be copied from F!
assaults.drop(['bula'], inplace=True, axis=1)
assaults.rename(columns={'date_d_mod':'date', 'location':'AGS'}, inplace=True)
assaults['date'] = pd.to_datetime(assaults['date'], format='%Y-%m-%d')

#keep only regions that are noe in the sample
assaults = assaults.merge(regions_in_use, on='AGS')

#keep only relevant variables
assaults = assaults[['date', 'AGS', 'ass', 'ass_f', 'ass_m', 'region_used']]



########## REGIONAL DATA BASE ##########
regional_data = pd.read_csv(z_prepared_data + 'regional_data_prepared.csv', sep=';', encoding='UTF-8')

#keep only regions that are noe in the sample
regional_data = regional_data.merge(regions_in_use, on='AGS')

# keep just important variables
regional_data = regional_data[['year', 'AGS', 'AGS_Name', 'pop_t']]

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


# merge Holidays
data = data.merge(holidays, on=['bula', 'date'], how='inner')


# merge Crime Data
data = data.merge(assaults, on=['date', 'AGS'], how='outer')
assaults_cols = assaults.columns.drop(['date', 'AGS', 'region_used']).tolist() # to fill nr assaults with zeros for NaNs
data[assaults_cols] = data[assaults_cols].fillna(value=0)


# merge Regional Data Base
data = data.merge(regional_data, on=['AGS', 'year'])

# merge Soccer data
data = data.merge(soccer2, on=['AGS', 'date'], how='outer',  indicator=True)
z_gameday_columns = ['D_away_game', 'D_home_game'] # gameday columns and interactions with gd
data[z_gameday_columns] = data[z_gameday_columns].fillna(0)


# up till here: dimension should be 96878 x 308




###############################################################################
#       Generate variables
###############################################################################

# generate assault rate
data['assrate']                 = (data['ass']                   * 1000000)/data['pop_t']

# assault rates per gender and age-group
data['assrate_f']               = (data['ass_f']                 * 1000000)/data['pop_t']
data['assrate_m']               = (data['ass_m']                 * 1000000)/data['pop_t']




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
z_number_obs_june = data.month[data.month == 6].count()
data.drop(data[data.month==6].index, inplace=True)


###############################################################################
#       Restrict number of variables
###############################################################################

data = data[[
        'date', 'AGS', 'AGS_Name', 'D_away_game', 'D_home_game',
        'assrate', 'assrate_f', 'assrate_m', 
        'bula', 'day', 'month', 'year', 'dow', 'doy', 'woy', 'days_in_year',
        'TMK', 'TXK', 'TNK', 'TGK', 'VPM', 'NM', 'PM', 'UPM', 'RS', 'SDK', 'SH', 'FM',
        'ferien', 'sch_hday', 'feiertag', 'pub_hday', 'special_day',
        'pop_t', 
        'league', 'season', 'gameday', 'team', 'opp_team'
        ]]



###############################################################################
#       Read out
###############################################################################
#data.to_csv(z_data_output + 'data_prepared.csv', sep=';', encoding='UTF-8', index=False)
data.to_csv(z_data_output_Dx + 'data_prepared_home_away.csv', sep=';', encoding='UTF-8', index=False)



###############################################################################
#       END OF FILE
###############################################################################
print("--- %s seconds ---" % (time.time() - start_time))





