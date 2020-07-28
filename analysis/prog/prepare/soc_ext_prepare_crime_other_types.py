# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 09:27:35 2020

@author: Marc Fabel


Description: generates overview of other types of crime. uses blue print of prepare_crime
    - used for robustness section

Inputs:
    - opfer-hashed-20XX.csv     cross-sections containing crime micro data
    - map_stadiums_AGS.csv      map: relates the stadiums to active regions - generated w/ QGIS
    - Schulferien_1015.dta      time series for all BL to see whether a part date is a holiday

Outputs:
    - crime_prepared.csv [intermed]

Updates:
    

"""

# packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time
start_time = time.time()


# paths (SERVER)
z_crime_source =        'F:/econ/soc_ext/analysis/data/source/BKA/opfer-hashed-'
z_maps_stadiums =       'F:/econ/soc_ext/analysis/data/intermediate/maps/'
z_crime_output =        'F:/econ/soc_ext/analysis/data/intermediate/crime/'
z_prefix =              'soc_ext_'


# paths (LOCAL) also irrelevant - cannot handle the data


# home paths irrelevant (data only on server)

# magic numbers
z_first_year_wave = 2011
z_last_year_wave = 2015

###############################################################################
#       1) Read in crime cross-sections, select assaults and append
###############################################################################


# COMMENT: first I only use cases where there is information up to the hour, can be refined later on


c = {}
for year in range(11,16):
    file = z_crime_source + '20' + str(year) + '/' + 'opfer-hashed-20' + str(year) + '.csv'
    c[year] = pd.read_csv(file, sep=';')
    c[year].rename(columns={
            'FALL_ID'                : 'case_id',
            'STRAFTATENSCHLUESSEL'   : 'offense_key',
            'BERICHTSDATUM'          : 'date_report',
            'VERSUCH'                : 'attempt',
            'TATZEIT_ENDE'           : 'date_offense',
            'TATORT_GEMEINDE'        : 'location',
            'TATORT_GROESSENKLASSE'  : 'location_size',
            'SCHUSSWAFFENVERWENDUNG' : 'firearm',
            'SCHADEN_ERLANGTES_GUT'  : 'loss_value',
            'PKS_SONDERKENNUNG'      : 'special_designation',
            'TV_ALLEINHANDELND'      : 'single_suspect',
            'ALTER_ZUR_TATZEIT'      : 'age',
            'GESCHLECHT'             : 'gender',
            'TV_BEZIEHUNG_FORMAL'    : 'vs_relation_formal',
            'TV_BEZIEHUNG_RML_SOZ'   : 'vs_relation_spatial_social',
            'SPEZIFIK'               : 'specific_role',
            'STAATSANGEHOERIGKEIT'   : 'citizenship',
            'GUELTIG_VON'            : 'date_validity'
     }, inplace =True)



# append CS and keep only relevant columns
offenses = c[11].copy()
for year in range(12,16):
    offenses = offenses.append(c[year])
offenses = offenses[['offense_key', 'date_offense', 'location']]                ## smaller version of DF


# make offense key string and add leading zeros
offenses['offense_key'] = offenses['offense_key'].astype(str)
offenses['offense_key'] = offenses['offense_key'].str.rjust(6, '0')

#temp =  offenses['offense_key'].astype(str).value_counts().to_frame()



#########   keep only relevant locations    #########

# first drop all offenses which are not recored in the 8 digit key - first correct if not adhere to 8 digit key (Bremen & Bremerhaven)
offenses.location = offenses.location.replace({
        4011 : 4011000,
        4012 : 4012000})
offenses.drop( offenses[offenses.location < 1000000].index, inplace=True)


# select only those which are active in the soccer project
stadiums_regions = pd.read_csv(z_maps_stadiums + 'map_stadiums_AGS.csv', sep=';')
active_regions = stadiums_regions.drop_duplicates(subset='AGS')
active_regions = active_regions['AGS'].copy().to_frame()
active_regions.sort_values('AGS', inplace=True)
active_regions.reset_index(inplace=True, drop=True)
active_regions['active'] = 1

offenses = offenses.merge(active_regions, left_on=['location'], right_on=['AGS'], how='inner')
offenses.drop(['AGS', 'active'], inplace=True, axis=1)









offenses.sort_values(['location', 'date_offense'], inplace=True)
# 








# keep if date is available
#offenses = offenses.loc[offenses['offense_key'] == 224000]
offenses['date_ymd'] = offenses['date_offense'].str.slice(0,8)
offenses['date_d'] = pd.to_datetime(offenses['date_ymd'], format='%Y%m%d', errors='coerce')
offenses['date_h'] = pd.to_datetime(offenses['date_offense'], format='%Y%m%d%H', errors='coerce')

# drop when day information is not available
offenses.drop( offenses[offenses.date_d.isnull()].index, inplace=True)


# modify the date: assign offenses happening between midnight and 6 am to the preceding day
def modify_day(date_h):
    if pd.isnull(date_h) is False:  # date_h is not missing
        hour = date_h.strftime("%H")
        if 0<= int(hour) <= 5:  # if incidence happened between 0:00 am and 5:59 am
            S = date_h - timedelta(days=1)
        else:
            S = date_h
    else:
        S = 'NaT'
    return S

offenses['temp'] = offenses.date_h.apply(lambda x: modify_day(x))
offenses['temp'].fillna(offenses.date_d, inplace=True)
offenses['date_off_mod_str'] = offenses.temp.apply(lambda x: x.strftime('%d%b%Y'))
offenses.drop(['date_ymd', 'date_d', 'temp'], axis=1, inplace=True)


# use only relevant time window: Januar 2011 - June 2015
offenses['date_d_mod'] = pd.to_datetime(offenses['date_off_mod_str'], format='%d%b%Y')
start = datetime(z_first_year_wave,1,1)
end = datetime(z_last_year_wave,6,30)
invalid_dates = offenses[ (offenses['date_d_mod'] < start) | (offenses['date_d_mod'] > end)].index
offenses.drop(invalid_dates, inplace=True)




offenses.drop(['date_offense', 'date_h', 'date_off_mod_str'], axis=1, inplace=True)





#########  generate variables    #########
offenses['all_offenses'] = 1

# other assaults
offenses['simple_bh'] = np.where(offenses.offense_key == '224000', 1, 0)
offenses['negligent_bh'] = np.where(offenses.offense_key == '225000', 1, 0)
offenses['dangerous_bh'] = np.where((offenses.offense_key == '222010') | (offenses.offense_key == '222110'), 1, 0)
offenses['grievous_bh']  = np.where((offenses.offense_key == '222020') | (offenses.offense_key == '222120'), 1, 0)
offenses['brawls_bh']    = np.where((offenses.offense_key == '222030') | (offenses.offense_key == '222130'), 1, 0)

# other violence
offenses['murder'] = np.where((offenses.offense_key == '010079') | (offenses.offense_key == '011000') | (offenses.offense_key == '012000'), 1, 0)
offenses['key_2'] = offenses['offense_key'].str.slice(0,2)
offenses['robbery'] = np.where(offenses.key_2 == '21', 1, 0)


# resistence to enforcement officers
offenses['resistence_enforcenebt'] = np.where((offenses.offense_key == '621021') | (offenses.offense_key == '621029'), 1, 0)


#  threats
offenses['threats'] = np.where(offenses.offense_key == '232300', 1, 0)

offenses.drop(['offense_key', 'key_2'], axis=1, inplace=True)






########## AGGREGATION ##########
# add up numbers of assaults per region
offenses = offenses.groupby(['date_d_mod','location']).sum()
offenses.reset_index(inplace=True, drop=False)



########## READING OUT ##########


offenses.to_csv(z_crime_output + 'crime_other_assault_types_prepared.csv', sep=';', encoding='UTF-8', index=False)










###############################################################################

# find error 
temp = c[11].loc[c[11].location == 1002000].copy()




temp = temp[['offense_key', 'date_offense', 'location']]
temp.sort_values('date_offense', inplace=True)
temp['offense_key'] = temp['offense_key'].astype(str)
temp['offense_key'] = temp['offense_key'].str.rjust(6, '0')


# keep if date is available
#temp = temp.loc[temp['offense_key'] == 224000]
temp['date_ymd'] = temp['date_offense'].str.slice(0,8)
temp['date_d'] = pd.to_datetime(temp['date_ymd'], format='%Y%m%d', errors='coerce')
temp['date_h'] = pd.to_datetime(temp['date_offense'], format='%Y%m%d%H', errors='coerce')

# drop when day information is not available
temp.drop( temp[temp.date_d.isnull()].index, inplace=True)


# modify the date: assign temp happening between midnight and 6 am to the preceding day
def modify_day(date_h):
    if pd.isnull(date_h) is False:  # date_h is not missing
        hour = date_h.strftime("%H")
        if 0<= int(hour) <= 5:  # if incidence happened between 0:00 am and 5:59 am
            S = date_h - timedelta(days=1)
        else:
            S = date_h
    else:
        S = 'NaT'
    return S

temp['temp'] = temp.date_h.apply(lambda x: modify_day(x))
temp['temp'].fillna(temp.date_d, inplace=True)
temp['date_off_mod_str'] = temp.temp.apply(lambda x: x.strftime('%d%b%Y'))
temp.drop(['date_ymd', 'date_d', 'temp'], axis=1, inplace=True)


# use only relevant time window: Januar 2011 - June 2015
temp['date_d_mod'] = pd.to_datetime(temp['date_off_mod_str'], format='%d%b%Y')
start = datetime(z_first_year_wave,1,1)
end = datetime(z_last_year_wave,6,30)
invalid_dates = temp[ (temp['date_d_mod'] < start) | (temp['date_d_mod'] > end)].index
temp.drop(invalid_dates, inplace=True)

temp.drop(['date_offense', 'date_h', 'date_off_mod_str'], axis=1, inplace=True)


temp['simple_bh'] = np.where(temp.offense_key == '224000', 1, 0)


temp.drop(['offense_key'], axis=1, inplace=True)

temp = temp.groupby(['date_d_mod','location']).sum()
temp.reset_index(inplace=True, drop=False)