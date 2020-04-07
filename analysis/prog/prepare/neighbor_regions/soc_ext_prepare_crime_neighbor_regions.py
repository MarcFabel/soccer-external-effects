# -*- coding: utf-8 -*-
"""
Created on Tue Apr 7 2020

@author: Marc Fabel


Inputs:
    - opfer-hashed-20XX.csv              cross-sections containing crime micro data
    - neighbor_regions_prepared.csv      map: relates the stadiums to active neighbor regions - generated w/ QGIS
    - Schulferien_1015.dta               time series for all BL to see whether a part date is a holiday

Outputs:
    - crime_neighbor_regions_prepared.csv [intermed]

comments:
    - this is a slim version of the normal prepare_crime file, in particular I 
    leave out the subcategories of assaults (age, relationship,...)

    
"""

# packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time
start_time = time.time()


# paths (SERVER)
z_crime_source =        'F:/econ/soc_ext/analysis/data/source/BKA/opfer-hashed-'
z_crime_figures_desc =  'F:/econ/soc_ext/analysis/output/graphs/descriptive/'
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
assaults = c[11].copy()
for year in range(12,16):
    assaults = assaults.append(c[year])
assaults = assaults[['offense_key', 'date_offense', 'location', 'attempt', 'age', 'gender', 'vs_relation_formal', 'vs_relation_spatial_social']]


# keep only assaults
assaults = assaults.loc[assaults['offense_key'] == 224000]
assaults['date_ymd'] = assaults['date_offense'].str.slice(0,8)
assaults['date_d'] = pd.to_datetime(assaults['date_ymd'], format='%Y%m%d', errors='coerce')
assaults['date_h'] = pd.to_datetime(assaults['date_offense'], format='%Y%m%d%H', errors='coerce')

# drop when day information is not available
assaults.drop( assaults[assaults.date_d.isnull()].index, inplace=True)


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

assaults['temp'] = assaults.date_h.apply(lambda x: modify_day(x))
assaults['temp'].fillna(assaults.date_d, inplace=True)
assaults['date_off_mod_str'] = assaults.temp.apply(lambda x: x.strftime('%d%b%Y'))
assaults.drop(['date_ymd', 'date_d', 'temp'], axis=1, inplace=True)
assaults.drop('offense_key', axis=1, inplace=True)


# use only relevant time window: Januar 2011 - June 2015
assaults['date_d_mod'] = pd.to_datetime(assaults['date_off_mod_str'], format='%d%b%Y')
start = datetime(z_first_year_wave,1,1)
end = datetime(z_last_year_wave,6,30)
invalid_dates = assaults[ (assaults['date_d_mod'] < start) | (assaults['date_d_mod'] > end)].index
assaults.drop(invalid_dates, inplace=True)


# make dummy variables
assaults['female'] = np.where(assaults.gender == 'W', 1, 0)
assaults['D_attempt'] = np.where(assaults.attempt == 'J', 1, 0)
assaults['vs_strangers'] = np.where((assaults.vs_relation_formal==500)
                                   | (assaults.vs_relation_formal==800), 1, 0)
assaults['domestic'] = np.where((assaults.vs_relation_spatial_social==110)
                                    | (assaults.vs_relation_spatial_social==190), 1, 0) #110erziehungsverhaeltnis 190 sonstiges verh. (ehepartner)
assaults.drop(['gender', 'attempt', 'vs_relation_formal', 'vs_relation_spatial_social'], inplace=True, axis=1)
assaults.rename(columns={'D_attempt' : 'attempt'}, inplace=True)




#########   keep only relevant locations    #########

# first drop all offenses which are not recored in the 8 digit key - first correct if not adhere to 8 digit key (Bremen & Bremerhaven)
assaults.location = assaults.location.replace({
        4011 : 4011000,
        4012 : 4012000})
assaults.drop( assaults[assaults.location < 1000000].index, inplace=True)


# select only those NEIGHBORING regions that are active in the soccer project
neighbor_regions = pd.read_csv(z_maps_stadiums + 'neighbor_regions_prepared.csv', sep=';')
active_neighbor_regions = neighbor_regions['AGS'].drop_duplicates().to_frame()
active_neighbor_regions.sort_values('AGS', inplace=True)
active_neighbor_regions.reset_index(inplace=True, drop=True)
active_neighbor_regions['active'] = 1

assaults = assaults.merge(active_neighbor_regions, left_on=['location'], right_on=['AGS'], how='inner')
assaults.drop(['AGS', 'active'], inplace=True, axis=1)


assaults_micro = assaults.copy()
assaults_micro['bula'] = assaults_micro.location.apply(lambda x: x/1000000).astype(int)



########## DEFINE SUBGROUPS ##########
assaults['ass_f'] = np.where(assaults.female == 1,1,0)
assaults['ass_m'] = np.where(assaults.female == 0,1,0)
#assaults['ass_0_17']  = np.where(assaults.age < 18,1,0)
#assaults['ass_18_29'] = np.where((assaults.age >= 18) & (assaults.age <=29),1,0)
#assaults['ass_30_39'] = np.where((assaults.age >= 30) & (assaults.age <=39),1,0)
#assaults['ass_40_49'] = np.where((assaults.age >= 40) & (assaults.age <=49),1,0)
#assaults['ass_50_59'] = np.where((assaults.age >= 50) & (assaults.age <=59),1,0)
#assaults['ass_60+']   = np.where(assaults.age >= 60,1,0)
#assaults['ass_vs_strangers'] = np.where(assaults.vs_strangers == 1,1,0)
#assaults['ass_vs_rel'] = np.where(assaults.vs_strangers == 0,1,0)
#assaults['ass_attempt'] = np.where(assaults.attempt == 1,1,0)
#assaults['ass_success'] = np.where(assaults.attempt == 0,1,0)
#assaults['ass_domestic'] = np.where(assaults.domestic == 1,1,0)
#
#assaults['ass_0_17_f']  = np.where((assaults.age < 18) & (assaults.female == 1),1,0)
#assaults['ass_18_29_f'] = np.where((assaults.age >= 18) & (assaults.age <=29) & (assaults.female == 1),1,0)
#assaults['ass_30_39_f'] = np.where((assaults.age >= 30) & (assaults.age <=39) & (assaults.female == 1),1,0)
#assaults['ass_40_49_f'] = np.where((assaults.age >= 40) & (assaults.age <=49) & (assaults.female == 1),1,0)
#assaults['ass_50_59_f'] = np.where((assaults.age >= 50) & (assaults.age <=59) & (assaults.female == 1),1,0)
#assaults['ass_60+_f']   = np.where((assaults.age >= 60) & (assaults.female == 1),1,0)
#assaults['ass_0_17_m']  = np.where((assaults.age < 18) & (assaults.female == 0),1,0)
#assaults['ass_18_29_m'] = np.where((assaults.age >= 18) & (assaults.age <=29) & (assaults.female == 0),1,0)
#assaults['ass_30_39_m'] = np.where((assaults.age >= 30) & (assaults.age <=39) & (assaults.female == 0),1,0)
#assaults['ass_40_49_m'] = np.where((assaults.age >= 40) & (assaults.age <=49) & (assaults.female == 0),1,0)
#assaults['ass_50_59_m'] = np.where((assaults.age >= 50) & (assaults.age <=59) & (assaults.female == 0),1,0)
#assaults['ass_60+_m']   = np.where((assaults.age >= 60) & (assaults.female == 0),1,0)
#
#assaults['ass_vs_strangers_f'] = np.where((assaults.vs_strangers == 1) & (assaults.female == 1),1,0)
#assaults['ass_vs_rel_f'] = np.where((assaults.vs_strangers == 0) & (assaults.female == 1),1,0)
#assaults['ass_domestic_f'] = np.where((assaults.domestic == 1) & (assaults.female == 1),1,0)
#assaults['ass_vs_strangers_m'] = np.where((assaults.vs_strangers == 1) & (assaults.female == 0),1,0)
#assaults['ass_vs_rel_m'] = np.where((assaults.vs_strangers == 0) & (assaults.female == 0),1,0)
#assaults['ass_domestic_m'] = np.where((assaults.domestic == 1) & (assaults.female == 0),1,0)


########## AGGREGATION ##########
# add up numbers of assaults per region
assaults['ass'] = 1
assaults = assaults.groupby(['date_d_mod','location']).sum()
assaults.reset_index(inplace=True, drop=False)
assaults.drop(['age', 'female', 'vs_strangers', 'attempt', 'domestic'], inplace=True, axis=1)
assaults['bula'] = assaults.location.apply(lambda x: x/1000000).astype(int)



########## READING OUT ##########
# reorder columns
z_cols_front = ['date_d_mod', 'location', 'bula', 'ass', 'ass_f', 'ass_m']
z_new_column_order = z_cols_front + (assaults.columns.drop(z_cols_front).tolist())
assaults = assaults[z_new_column_order]

assaults.to_csv(z_crime_output + 'crime_neighbor_regions_prepared.csv', sep=';', encoding='UTF-8', index=False)




temp = assaults.location.value_counts()

