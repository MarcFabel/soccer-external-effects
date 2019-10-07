# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 16:36:35 2019

@author: fabel

This file combines all the prepared data files in a wide format on the AGS-day level




"""

# packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#from matplotlib.dates import DateFormatter
#import matplotlib.style as style
#style.available
#style.use('seaborn-darkgrid')


# paths
z_holidays =            'F:/econ/soc_ext/analysis/data/final/holidays/'
z_crime_intermed =      'F:/econ/soc_ext/analysis/data/intermediate/crime/'
z_weather =             'F:/econ/soc_ext/analysis/data/intermediate/weather/'
z_regional_data =       'F:/econ/soc_ext/analysis/data/intermediate/regional_database/'
z_prefix =              'soc_ext_'



# magic numbers
z_first_year_wave = 2011
z_last_year_wave = 2015

###############################################################################
#       1) Read in data frames
###############################################################################



########## HOLIDAYS ##########
holidays = pd.read_stata(z_holidays + 'Schulferien_1015.dta')
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


########## WEATHER ##########
weather = pd.read_csv(z_weather + 'weather_prepared.csv', sep=';', encoding='UTF-8')
# cut weather to the right time window
weather['date'] = pd.to_datetime(weather['date'], format='%Y-%m-%d')
weather.drop( weather[  (weather.date < start) | (weather.date > end)].index, inplace=True)
weather.drop(['Unnamed: 0'], inplace=True, axis=1)


########## CRIME ##########
assaults = pd.read_csv(z_crime_intermed + 'crime_prepared.csv', sep=';', encoding='UTF-8')
assaults.drop(['bula'], inplace=True, axis=1)
assaults.rename(columns={'date_d_mod':'date', 'location':'AGS'}, inplace=True)
assaults['date'] = pd.to_datetime(assaults['date'], format='%Y-%m-%d')


########## REGIONAL DATA BASE ##########
regional_data = pd.read_csv(z_regional_data + 'regional_data_prepared.csv', sep=';', encoding='UTF-8')


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


# merge other data frames to it
data = data.merge(holidays, on=['bula', 'date'], how='outer')
data = data.merge(assaults, on=['date', 'AGS'], how='outer')
data.offences.fillna(0, inplace=True)
data = data.merge(regional_data, on=['AGS', 'year'])

# merge soccer






# generate offense rates









###############################################################################
#       END OF FILE
###############################################################################


# XXX TO DO:
# regional_data: finish with generating the variables from other columns and drop irrelevnt ones, as they serve as input elsewhere
# for a later time: kick weird stadiums out
# ACTIVE REGIONS ARE NOT ACTIVE ALL THE TIME, IN SOME YEARS SOME TEAMS ARE NOT EVEN PART OF THE THIRD LEAGUE



