# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:25:50 2019

@author: Fabel

Steps:

     1) read in the time series for all of the variables and generate a wide
     version, i.e. a panel on the monitor-day level

     2) use the monitors, which are present at all of the observed years and which
     observe all the weather variables at the same time (see comment below) and
     find with QGIS the nearest associated weather monitor to each stadium.
     use that as input to restrict the wide weather df to the relevant monitors.
     -> exported as weather_prepare to Dropbox
     
Inputs:  
    a) map_stadium_nearest_weather_monitor.csv
         - comes as output from QGIS, generated by "Distance to nearest hub" has to be copied from DX
         - maps the stadiums to the nearest weather monitor
         - in an earlier version of the program, it was read_in directly from Dx
         
Updates: 26/09/2019: 
    a) error in building up the weather df, merge has to be outer, otherwise it drops dates from the df! 
    b) NaNs in the column are no filled with preceeding values
     
"""

# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.style as style


# paths work
z_weather_source =                      'F:/econ/soc_ext/analysis/data/source/weather/cdc_download_2019-08-28_11-40/data/'
z_weather_output_Dx =                   'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/weather/'
z_weather_output =                      'F:/econ/soc_ext/analysis/data/intermediate/weather/'
z_map_stadium_weather_monitor_input =   'F:/econ/soc_ext/analysis/data/intermediate/maps/' 
z_weather_figures_desc =                'F:/econ/soc_ext/analysis/output/graphs/descriptive/'
z_prefix =                              'soc_ext_'


# HOME directories
#z_weather_output_Dx = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/weather/'
#z_map_stadium_weather_monitor_input = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/' # comes as output from QGIS, generated by "Distance to nearest hub"
#soccer_output = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/soccer/'




# magic numbers
first_year_wave = 2010
last_year_wave = 2015



###############################################################################
#       1)    Read in and merge the data
###############################################################################

# generate empty lists -> used to construct df that contains # of monitors for each var
lst_var = []
lst_number_monitors = []

j = 1
for var in ['TMK', 'TXK', 'TNK', 'TGK', 'VPM', 'NM', 'PM', 'UPM', 'RS', 'SDK', 'SH', 'FM']: #
     print(var)
     data = pd.read_csv(z_weather_source + 'data_' + var + '.csv', sep=',', encoding = 'UTF-8')
     data.drop(['Produkt_Code','Qualitaet_Niveau', 'Qualitaet_Byte'], axis=1, inplace=True)
     data.rename(columns={'Zeitstempel':'date'}, inplace=True)
     data['year'] = pd.to_numeric(data['date'].astype(str).str.slice(0,4))
     delete_rows = data[ (data['year']<first_year_wave) | (data['year']>last_year_wave) ].index
     data.drop(delete_rows, inplace=True)
     data.drop('year', axis=1, inplace=True)
     data.rename(columns={'Wert':var}, inplace=True)

     sdo = pd.read_csv(z_weather_source + 'sdo_' + var + '.csv', sep=',', encoding = 'UTF-8')
     sdo.drop(['Metadata_Link', 'Hoehe_ueber_NN'], axis=1, inplace=True)
     sdo.rename(columns={'Geogr_Laenge':'geo_x', 'Geogr_Breite':'geo_y'}, inplace=True)

     lst_var.append(var)
     lst_number_monitors.append(len(sdo))

     # merge data and sdo together
     data = data.merge(sdo, on=['SDO_ID'])

     # put together final data set
     if j == 1:
          weather = data
          j = j + 1
     else:
          weather = weather.merge(data, on=['SDO_ID', 'SDO_Name', 'geo_x', 'geo_y', 'date'], how='outer')

dictionary = {'variable': lst_var, 'number_monitors': lst_number_monitors}
df_number_monitors = pd.DataFrame(dictionary)



###############################################################################
#       2 ) Weather monitors & their distance to stadiums
###############################################################################

monitors = weather.drop_duplicates(subset='SDO_ID')
monitors = monitors[['SDO_ID', 'date', 'SDO_Name', 'geo_x', 'geo_y']].copy()

# drop monitors which are not present over the entire period:
delete_rows = monitors[ (monitors['date'] != 20110101) ].index
monitors.drop(delete_rows, inplace=True)
monitors['D_all_years'] = 1

# read out
monitors.to_csv(z_weather_output + 'weather_monitors_coordinates_outer_merge.csv', sep=';', encoding='UTF-8')   #name and location changed 26/09/2019


# now go to QGIS and look for the nearest stadium-monitor pair and use only subset of monotors for output
# has to create     map_stadium_nearest_weather_monitor.csv'

# open up edited stadium-monitor pair
stadium_monitor = pd.read_csv(z_map_stadium_weather_monitor_input + 'map_stadium_nearest_weather_monitor.csv', sep=';', encoding = 'UTF-8')
stadium_monitor.drop(['field_1', 'Koordinaten_Nord', 'Koordinaten_Ost', 'PLZ', 'Straße', 'Hausnummer', 'games_played'], axis=1, inplace=True)
stadium_monitor.rename(columns={'HubName':'SDO_ID', 'HubDist':'distance_closest_sdo'}, inplace=True)


# merge with weather data (inner)
weather = weather.merge(stadium_monitor, on=['SDO_ID'], how='inner')





###############################################################################
#       3 ) HANDLING OF MISSING DATA
###############################################################################
weather['date'] = pd.to_datetime(weather['date'], format='%Y%m%d')  
weather['month'] = weather.date.apply(lambda x: x.strftime('%m')).astype(int)      

# fill missings of SH (snow height) in summer with zeros: 
make_zeros = (weather.SH.isnull()) & (weather.month >4) & (weather.month < 10)
weather.loc[make_zeros, 'SH'] = 0

# Which variables have the most missing - see description
for var in ['TMK', 'TXK', 'TNK', 'TGK', 'VPM', 'NM', 'PM', 'UPM', 'RS', 'SDK', 'SH', 'FM']:
    print(weather[var].isnull().value_counts())

 # use forward fill - i.e. if one value of one monitor is missing
 #  then it will use the value of the preceding day 
 # copy across monitors is not a problem as the time window is too wide
for var in weather[['TMK', 'TXK', 'TNK', 'TGK', 'VPM', 'NM', 'PM', 'UPM', 'RS', 'SDK', 'SH', 'FM']]:
    weather[var].fillna(method='ffill', inplace=True)





###############################################################################
#       4 ) read out
###############################################################################
# sort & order
weather = weather[[
     'date', 'stadium', 'Ort', 'SDO_ID', 'SDO_Name',
     'TMK', 'TXK', 'TNK', 'TGK', 'VPM', 'NM', 'PM', 'UPM', 'RS', 'SDK', 'SH', 'FM',
     'distance_closest_sdo', 'geo_x', 'geo_y']]

weather.sort_values(['Ort','date'], inplace=True)

# drop variables
weather.drop(['geo_x', 'geo_y'], axis=1, inplace=True)


# read out
weather.to_csv(z_weather_output + 'weather_prepared.csv', sep=';', encoding='UTF-8')


# MISSING: WHAT IS THE AGS OF THE RESPECTIVE STADIUM

###############################################################################
#       5) Plotting distance of weather monitors to stadiums
###############################################################################



style.available
style.use('seaborn-darkgrid')

#style.use('seaborn-paper') # alternative talk and presentation - makes it bigger
#sns.set_context('paper')


# histogram unweighted
sns.distplot(stadium_monitor['distance_closest_sdo'], hist=True, kde=False, norm_hist=True,
             bins=int(50/4), color = 'darkblue',
             hist_kws={'edgecolor':'black'})

plt.xlabel('Distance [km]')
plt.ylabel('Density') # 'Number of monitor-stadium pairs'

plt.savefig(z_weather_figures_desc + z_prefix + 'distance_monitors_stadiums.pdf')


###############################################################################
#           END OF FILE
###############################################################################



# to do: what shall I do with NANs in the columns

# Comments:
# - first I use the subset of monitors that have all the variables over all years
#    at a later robustness check, one could refine that approach: i.e. what is per
#    variable the closest monitor, have a weather_variable-specific stadium-monitor
#    match








# OLD:
# 1) Plotting
# other approach
#bins = np.arange(0,50,4)
#hist, edges = np.histogram(stadium_monitor['distance_closest_sdo'], bins)
#freq = hist/float(hist.sum())
#plt.bar(bins[:-1], freq, width=4, align="edge", ec="k" )
#plt.show()
#
#sns.barplot(bins[:-1], freq)
#
#
#
## weighted in how foten it appears in the data
#df = pd.read_csv(soccer_output + 'soccer_prepared.csv', sep=';')
#df = df.merge(stadium_monitor, on='stadium')
#
#sns.distplot(df['distance_closest_sdo'], hist=True, kde=False, norm_hist=True,
#             bins=int(50/4), color = 'darkblue',
#             hist_kws={'edgecolor':'black'})
#
#plt.title('Histogram of Distances from weather monitor to stadiums')
#plt.xlabel('Distance (km)')
#plt.ylabel('Number of monitor-stadium pairs')
