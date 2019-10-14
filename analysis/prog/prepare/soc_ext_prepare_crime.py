# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 12:18:55 2019

@author: Marc Fabel


Inputs:
    - opfer-hashed-20XX.csv     cross-sections containing crime micro data
    - map_stadiums_AGS.csv      map: relates the stadiums to active regions - generated w/ QGIS
    - Schulferien_1015.dta      time series for all BL to see whether a part date is a holiday

Outputs:
    -

"""

# packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import matplotlib.style as style
#style.available
style.use('seaborn-darkgrid')
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
assaults = assaults[['offense_key', 'date_offense', 'location', 'attempt', 'age', 'gender', 'vs_relation_formal']]


# keep only assaults & only when offense date is in 2014
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
assaults.rename(columns={'D_attempt' : 'attempt'}, inplace=True)
assaults['vs_strangers'] = np.where((assaults.vs_relation_formal==500)
                                   | (assaults.vs_relation_formal==800), 1, 0)
assaults.drop(['gender', 'attempt', 'vs_relation_formal'], inplace=True, axis=1)




#########   keep only relevant locations    #########

# first drop all offenses which are not recored in the 8 digit key - first correct if not adhere to 8 digit key (Bremen & Bremerhaven)
assaults.location = assaults.location.replace({
        4011 : 4011000,
        4012 : 4012000})
assaults.drop( assaults[assaults.location < 1000000].index, inplace=True)


# select only those which are active in the soccer project
stadiums_regions = pd.read_csv(z_maps_stadiums + 'map_stadiums_AGS.csv', sep=';')
active_regions = stadiums_regions.drop_duplicates(subset='AGS')
active_regions = active_regions['AGS'].copy().to_frame()
active_regions.sort_values('AGS', inplace=True)
active_regions.reset_index(inplace=True, drop=True)
active_regions['active'] = 1

assaults = assaults.merge(active_regions, left_on=['location'], right_on=['AGS'], how='inner')
assaults.drop(['AGS', 'active'], inplace=True, axis=1)



assaults_micro = assaults.copy()
assaults_micro['bula'] = assaults_micro.location.apply(lambda x: x/1000000).astype(int)



########## AGGREGATION ##########
# add up numbers of assaults per region
assaults['assaults'] = 1
assaults = assaults.groupby(['date_d_mod','location']).sum()
assaults.reset_index(inplace=True, drop=False)
assaults.drop(['age', 'female', 'vs_strangers'], inplace=True, axis=1)
assaults['bula'] = assaults.location.apply(lambda x: x/1000000).astype(int)



########## READING OUT ##########
assaults.to_csv(z_crime_output + 'crime_prepared.csv', sep=';', encoding='UTF-8', index=False)





###############################################################################
#       2) Explorative Data Analysis
###############################################################################


########## OVER THE DAY ##########
# over the course of the day (how many cases are dropped, i.e. fraction where there is no information on the hour)
# special drop cases where there is no hour dimension:   assaults.date_h.isnull().astype(int).mean()

ass_h = assaults_micro.drop(assaults_micro[assaults_micro.date_h.isnull()].index)
ass_h['hour'] = ass_h.date_h.apply(lambda x: x.strftime('%H'))

ass_h = ass_h['hour'].astype(str).value_counts().to_frame()
ass_h.reset_index(inplace=True, drop=False)
ass_h.rename(columns={'index':'hour', 'hour':'counts'}, inplace=True)

temp_hours = {
    'hour' : ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '00', '01', '02', '03', '04', '05'],
    'hour_num' : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]}
temp_hours = pd.DataFrame(temp_hours)
ass_h = ass_h.merge(temp_hours, on=['hour'])

ass_h['freq'] = ass_h['counts']/float(ass_h['counts'].sum())
ass_h.sort_values(['hour_num'], inplace=True, ascending=True)
ass_h.reset_index(inplace=True, drop=True)
#plot
ax = sns.barplot(ass_h.hour_num, ass_h.freq, color = 'darkblue')
ax.set(xlabel='', ylabel='Relative frequency') #xlabel='months',
ax.set_xticklabels(ass_h.hour)
plt.title("Panel A: Assaults across the course of a day", fontweight="bold", loc='left')
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_crime_figures_desc + z_prefix + 'assaults_per_hour.pdf')




########## OVER THE WEEK ##########
ass_dow = assaults_micro.copy()
ass_dow['dow'] = ass_dow.date_d_mod.apply(lambda x: x.strftime('%a'))
ass_dow = ass_dow['dow'].astype(str).value_counts().to_frame()
ass_dow.reset_index(inplace=True, drop=False)
ass_dow.rename(columns={'index':'dow', 'dow':'counts'}, inplace=True)
temp_dows = {
    'dow' : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    'dow_num' : [1,2,3,4,5,6,7]}
temp_dows = pd.DataFrame(temp_dows)
ass_dow = ass_dow.merge(temp_dows, on=['dow'])
ass_dow['freq'] = ass_dow['counts']/float(ass_dow['counts'].sum())
ass_dow.sort_values(['dow_num'], inplace=True, ascending=True)
#plot
ax = sns.barplot(ass_dow.dow, ass_dow.freq, color = 'darkblue')
ax.set(xlabel='', ylabel='Relative frequency') #xlabel='months',
plt.title("Panel B: Assaults across days of the week", fontweight="bold", loc='left')
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_crime_figures_desc + z_prefix + 'assaults_per_dow.pdf')





########## OVER THE months ##########
ass_month = assaults_micro.copy()
# keep only 2014
start = datetime(2014,1,1)
end = datetime(2014,12,31)
invalid_dates = ass_month[ (ass_month['date_d_mod'] < start) | (ass_month['date_d_mod'] > end)].index
ass_month.drop(invalid_dates, inplace=True)

ass_month['month'] = ass_month.date_d_mod.apply(lambda x: x.strftime('%b'))

ass_month = ass_month['month'].astype(str).value_counts().to_frame()
ass_month.reset_index(inplace=True, drop=False)
ass_month.rename(columns={'index':'month', 'month':'counts'}, inplace=True)
temp_months = {
    'month' : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    'month_num' : [1,2,3,4,5,6,7,8,9,10,11,12],
    'days'  : [31,28,31,30,31,30,31,31,30,31,30,31]}
temp_months = pd.DataFrame(temp_months)
ass_month = ass_month.merge(temp_months, on=['month'])
ass_month['counts_norm']= ass_month.counts / ass_month.days

ass_month['freq'] = ass_month['counts']/float(ass_month['counts'].sum())
ass_month['freq_norm'] = ass_month['counts_norm']/float(ass_month['counts_norm'].sum())
ass_month.sort_values(['month_num'], inplace=True, ascending=True)
#plot
ax = sns.barplot(ass_month.month, ass_month.freq_norm, color = 'darkblue')
ax.set(xlabel='', ylabel='Relative frequency') #xlabel='months',
plt.title("Panel C: Assaults across months of the year $^1$", fontweight="bold", loc='left')
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_crime_figures_desc + z_prefix + 'assaults_per_month_2014.pdf')






########## OVER THE YEAR ##########
ass_day = assaults_micro.copy()
ass_day = ass_day['date_d_mod'].value_counts().to_frame()
ass_day.reset_index(inplace=True, drop=False)
ass_day.rename(columns={'index':'date_d_mod', 'date_d_mod':'counts'}, inplace=True)

# keep only 2014
invalid_dates = ass_day[ (ass_day['date_d_mod'] < start) | (ass_day['date_d_mod'] > end)].index
ass_day.drop(invalid_dates, inplace=True)

ass_day['freq'] = ass_day['counts']/float(ass_day['counts'].sum())
ass_day.sort_values(['date_d_mod'], inplace=True, ascending=True)
ass_day.reset_index(inplace=True, drop=True)

ax = sns.lineplot(ass_day.date_d_mod, ass_day.freq, color = 'darkblue')   #, kind='line'
ax.set(xlabel='', ylabel='Relative frequency') #xlabel='months',
plt.title("Panel D: Assaults across days of the year $^1$", fontweight="bold", loc='left')
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_crime_figures_desc + z_prefix + 'assaults_per_day_2014_single.pdf')




########## OVER THE YEAR - FOR ALL YEARS ##########
ass_day = assaults_micro.copy()
ass_day = ass_day['date_d_mod'].value_counts().to_frame()
ass_day.reset_index(inplace=True, drop=False)
ass_day.rename(columns={'index':'date_d_mod', 'date_d_mod':'counts'}, inplace=True)
ass_day['freq'] = ass_day['counts']/float(ass_day['counts'].sum())
ass_day.sort_values(['date_d_mod'], inplace=True, ascending=True)
ass_day.reset_index(inplace=True, drop=True)
ass_day['day'] = ass_day.date_d_mod.apply(lambda x: x.strftime('%d'))
ass_day['month'] = ass_day.date_d_mod.apply(lambda x: x.strftime('%m'))
ass_day['year'] = ass_day.date_d_mod.apply(lambda x: x.strftime('%Y'))
ass_day['d_m'] = ass_day.month + '-' + ass_day.day

# pivot table and merge again to ass_day df
temp = ass_day.pivot(index='d_m', columns='year', values='freq')
temp.reset_index(inplace=True, drop=False)

start = datetime(2012,1,1)
end = datetime(2012,12,31)
invalid_dates = ass_day[ (ass_day['date_d_mod'] < start) | (ass_day['date_d_mod'] > end)].index
ass_day.drop(invalid_dates, inplace=True)

# merge temp to ass_day
ass_day.drop(['counts', 'freq', 'day', 'month', 'year'], inplace=True, axis=1)
ass_day = ass_day.merge(temp, on=['d_m'], how='outer')
ass_day.drop('d_m', inplace=True, axis=1)

#plot
dct = {2011:'darkblue', 2012:'darkred', 2013:'darkgreen', 2014:'darkorange', 2015:'yellow'}
for year in range(2011,2016):
    fig, ax = plt.subplots()
    ax.plot(ass_day['date_d_mod'], ass_day[str(year)], marker='', color=dct[year], linewidth=1.0, alpha=0.9)
    for v in ass_day.drop('date_d_mod', axis=1):
        ax.plot(ass_day['date_d_mod'], ass_day[v], marker='', color='grey', linewidth=0.3, alpha=0.3)
    ax.xaxis.set_major_formatter(DateFormatter("%m"))
    ax.set_yticks(np.arange(0, 0.0025, 0.0005))
    plt.title(str(year), fontweight="bold", loc='center')
    plt.savefig(z_crime_figures_desc + z_prefix + 'assaults_per_day_' + str(year) + '.pdf')






















########## FREQUENCY OF OFFENSE TYPES ##########
offenses = c[14]['offense_key'].astype(str).value_counts().to_frame()
offenses.reset_index(inplace=True, drop=False)
offenses.rename(columns={'index':'offense_key', 'offense_key':'counts'}, inplace=True)
offenses['freq'] = offenses['counts']/float(offenses['counts'].sum())
offenses = offenses[:19]
offenses.sort_values(['counts'], inplace=True, ascending=False)


# 2011
# the four most common offenses comprise 71 % of the cases. 10 most common correspond to 90% of all cases
# there are in total 116 different keys in use

#------------------------------------------------------------------------------------------------------------------------
# offense_key	counts    PKS-Katalog(Schlüssel-Straftaten)                       PCS-report(english equivalent)
#------------------------------------------------------------------------------------------------------------------------
#0	224000	408703        ::Vorsätzliche einfache Körperverletzung § 223 StGB   intentional simple bodily injury
#1	232300	112270        :::Bedrohung § 241 StGB                                   threat (offenses against personal freedom)
#2	222110	84095         ::::Gefährliche Körperverletzung gemäß § 224 StGB auf Straßen, Wegen oder Plätzen
#3	222010	83927         :::Sonstige Tatörtlichkeit bei gefährlicher Körperverletzung gemäß § 224 StGB
#4	621021	38637         ::::Widerstand gegen Polizeivollzugsbeamte
#5	232279	35501         ::::Sonstige Nötigung gemäß § 240 Abs. 1 und 4 StGB
#6	232201	33098         ::::Nötigung im Straßenverkehr gemäß § 240 Abs. 1 StGB
#7	232410	26460         ::::Nachstellung (Stalking) gemäß § 238, Abs. 1 StGB
#8	225000	24544         ::fahrlässige Körperverletzung § 230 StGB
#9	217010	13962         :::Sonstiger Raub auf Straßen, Wegen oder Plätzen § 249 StGB

# same elements are in 2015, maybe different ordering


#plot
#plt.figure() ## figsize=(6,4)
ax = sns.barplot(offenses.index, offenses.freq, palette='Blues_d') #
ax.set(xlabel='Offense key', ylabel='Relative frequency')
ax.set_xticklabels(offenses.offense_key)
for item in ax.get_xticklabels():
     item.set_rotation(90)
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_crime_figures_desc + z_prefix + 'offense_key_distribution_2014.pdf')












###############################################################################
#       END OF FILE
###############################################################################
print("--- %s seconds ---" % (time.time() - start_time))



# XXX To Do:
#   - browse throug prepare programs and put figures in seperate analysis programs
#   - number of assaults per gender, potentially also other dimensions when easily inplementable


# next steps:
# hat mit den locations alles gepasst - number of assaults pro tag n bischen arg gering, oder?
# checken ob Karneval im holiday datensatz ist
# time series of dates und co anf"ugen
# article about any and all() for cleaning
# put in Figure of weather distance to stadiums in LaTeX document
# sch"one rumspielerei: spatial dimension of assault rates in combination with QGIS


# comments:
# - sind die Variablen über die Zeit konstant: PKS report: uspect under the influence of alcohol & hard drug users
#       appearantly yes, as the columns do not change between 2011 and 2015
# - citizenship from 2013 onwards















