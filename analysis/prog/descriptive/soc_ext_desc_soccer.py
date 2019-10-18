# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 14:26:21 2019

@author: Fabel
"""


# packages
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.ticker
import matplotlib.pyplot as plt
import matplotlib.style as style
#from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

import datetime
#style.available
style.use('seaborn-darkgrid')

# paths
z_prepared_data =             'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_figures_desc =              'F:/econ/soc_ext/analysis/output/graphs/descriptive/'
z_prefix =                    'soc_ext_'



data = pd.read_csv(z_prepared_data + 'data_prepared.csv', sep=';', encoding='UTF-8')



###############################################################################
#       Game days across days of the week
###############################################################################
matches = data[data['D_gameday']== 1]

games_dow = matches['dow'].value_counts().to_frame()
games_dow.reset_index(inplace=True, drop=False)
games_dow.rename(columns={'index':'dow', 'dow':'counts'}, inplace=True)
temp_dows = {
    'dow' : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    'dow_num' : [1,2,3,4,5,6,7]}
temp_dows = pd.DataFrame(temp_dows)
games_dow = games_dow.merge(temp_dows, on=['dow'])
games_dow['freq'] = games_dow['counts']/float(games_dow['counts'].sum())
games_dow.sort_values(['dow_num'], inplace=True, ascending=True)
#plot
ax = sns.barplot(games_dow.dow, games_dow.freq, color = 'darkblue')
ax.set(xlabel='', ylabel='Relative frequency') #xlabel='months',
plt.tight_layout()      # makes room for the x-label (as it is quite wide)
plt.savefig(z_figures_desc + z_prefix + 'games_per_dow.pdf')



# games over the course of the day (by weekend, by weekday)
spectators = matches[['league', 'date', 'attendance', 'stadium', 'time', 'dow']].copy()
spectators['weekend'] = np.where((spectators.dow == 'Sat') | (spectators.dow == 'Sun'),1,0)



#############
# stackoverflow
spectators['hour']=pd.to_datetime(spectators['time'],format='%H:%M')
temp = spectators['hour'].groupby(spectators['hour']).count().to_frame()

temp = spectators.groupby(['hour', 'weekend']).count()
temp.reset_index(inplace=True, drop=False)
temp.set_index('hour', drop=False, inplace=True)

ax = sns.barplot(temp.index, temp.date, hue=temp.weekend)
ticklabels = temp.index.strftime('%H:%M')
ax.xaxis.set_major_locator(mdates.HourLocator(interval = 1))
ax.xaxis.set_major_formatter(matplotlib.ticker.FixedFormatter(ticklabels))
#ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.tight_layout()

# tick frequency einstellen

fig, ax = plt.subplots()
ax = sns.barplot(temp.index, temp.date, hue=temp.weekend)
hours = mdates.HourLocator(interval = 1)
h_fmt = mdates.DateFormatter('%H:%M:%S')
ax.xaxis.set_major_locator(hours)
ax.xaxis.set_major_formatter(h_fmt)
fig.autofmt_xdate()
plt.show()


# evtl als kdensity
spectators.set_index('hour', inplace=True, drop=False)
ax = sns.distplot(temp.index)

###############################################################################
#       Spectators per league
###############################################################################


spectators['league'] = spectators['league'].astype(int)
spectators['attendance'] = spectators['attendance']/1000

ax = sns.catplot(x='league', y='attendance', data=spectators, kind='violin',
                 palette='Blues', inner='box')
ax.set(xlabel='League', ylabel='Attendance [in thousand]')
plt.savefig(z_figures_desc + z_prefix + 'attendance_per_league.pdf')




###############################################################################
#       Assaults - per gameday and non-gameday
###############################################################################

#  average number of offences per weekday on a game day and normal day



