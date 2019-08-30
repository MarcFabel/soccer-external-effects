# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:59:13 2019

@author: Fabel
"""

#packages
import pandas as pd

#paths & magic numbers
soccer_data = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/soccer/webscraping/output/'


# HOME directories 
#soccer_data = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/soccer/webscraping/output/'

#magic numbers
first_year_wave = 2010
last_year_wave = 2014



###############################################################################
# read in all leagues from season 2010/11 untill 2014/15, generate one league file



########## league 1 ##########
l1 = pd.read_csv(soccer_data + 'cross-sections/' + 'kicker_matchday_bl_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l1_temp = pd.read_csv(soccer_data + 'cross-sections/' + 'kicker_matchday_bl_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
    l1 = l1.append(l1_temp)
l1['league']= 1
l1.reset_index(inplace=True, drop=True)


# cleaning von Liga 1 duplicates (verlegte Spiele)
doubling = l1[ (l1['season'] == '2010-11') & (l1['gameday'] == 22) & (l1['home_team'] == 'HSV')].index
l1.drop(doubling, inplace=True)
doubling = l1[ (l1['season'] == '2011-12') & (l1['gameday'] == 16) & (l1['away_team'] == 'Mainz')].index
l1.drop(doubling, inplace=True)
doubling = l1[ (l1['season'] == '2013-14') & (l1['gameday'] == 18) & (l1['home_team'] == 'Stuttgart') & (l1['away_team'] == 'Bayern')].index
l1.drop(doubling, inplace=True)

# merge delayed games
l1_delayed = pd.read_csv(soccer_data + 'kicker_matchdayresults_delayedgames_bl.csv', sep=';', encoding='ISO-8859-1')
l1_delayed['season_first_number'] = pd.to_numeric(l1_delayed['season'].str.slice(0,4))
delete_entries = l1_delayed[  (l1_delayed['season_first_number']<first_year_wave) | ((l1_delayed['season_first_number']>last_year_wave))  ].index
l1_delayed.drop(delete_entries, inplace=True)
l1_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l1_delayed['D_delayed'] = 1
l1_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l1 = l1.merge(l1_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l1['D_delayed'].fillna(value=0, inplace=True)



########## league 2 ##########
l2 = pd.read_csv(soccer_data + 'cross-sections/' + 'kicker_matchday_2l_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l2_temp = pd.read_csv(soccer_data + 'cross-sections/' + 'kicker_matchday_2l_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
    l2 = l2.append(l2_temp)
l2['league']= 2
l2.reset_index(inplace=True, drop=True)

# merge delayed games
l2_delayed = pd.read_csv(soccer_data + 'kicker_matchdayresults_delayedgames_2l.csv', sep=';', encoding='ISO-8859-1')
l2_delayed['season_first_number'] = pd.to_numeric(l2_delayed['season'].str.slice(0,4))
delete_entries = l2_delayed[  (l2_delayed['season_first_number']<first_year_wave) | ((l2_delayed['season_first_number']>last_year_wave))  ].index
l2_delayed.drop(delete_entries, inplace=True)
l2_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l2_delayed['D_delayed'] = 1
l2_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l2 = l2.merge(l2_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l2['D_delayed'].fillna(value=0, inplace=True)

# rename team names (correct for scraping mistakes)
l2.home_team = l2.home_team.replace({'öln':'Köln'})



########## league 3 ##########
l3 = pd.read_csv(soccer_data + 'kicker_matchday_3l.csv', sep=';', encoding='ISO-8859-1')
l3['league'] = 3
l3['season_first_number'] = pd.to_numeric(l3['season'].str.slice(0,4))

delete_entries = l3[ (l3['season_first_number']<first_year_wave) |  (l3['season_first_number']>last_year_wave) ].index
l3.drop(delete_entries, inplace=True)
l3.drop('season_first_number', axis=1, inplace=True)
l3.reset_index(inplace=True, drop=True)

# rename team names (correct for scraping mistakes)
l3.home_team = l3.home_team.replace({'SaarbrÃ¼cken': 'Saarbrücken',
                                      'MÃ¼nster': 'Münster',
                                      'GroÃaspach': 'Großaspach',
                                      'OsnabrÃ¼ck': 'Osnabrück',
                                      'F. KÃ¶ln': 'Fortuna Köln'})
l3.away_team = l3.away_team.replace({'SaarbrÃ¼cken': 'Saarbrücken',
                                      'MÃ¼nster': 'Münster',
                                      'GroÃaspach': 'Großaspach',
                                      'OsnabrÃ¼ck': 'Osnabrück',
                                      'F. KÃ¶ln': 'Fortuna Köln'})

# merge delayed games
l3_delayed = pd.read_csv(soccer_data + 'kicker_matchdayresults_delayedgames_3l.csv', sep=';', encoding='ISO-8859-1')
l3_delayed['season_first_number'] = pd.to_numeric(l3_delayed['season'].str.slice(0,4))
delete_entries = l3_delayed[  (l3_delayed['season_first_number']<first_year_wave) | ((l3_delayed['season_first_number']>last_year_wave))  ].index
l3_delayed.drop(delete_entries, inplace=True)
l3_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l3_delayed['D_delayed'] = 1
l3_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l3 = l3.merge(l3_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l3['D_delayed'].fillna(value=0, inplace=True)









########## rename columns ##########
l1.rename(columns={'               home_result_end':'home_result_end',
                   '               stadium':'stadium',
                   '               goal_order':'goal_order',
                   '               away_yellow':'away_yellow',
                   '               home_ball':'home_ball'}, inplace=True)
    
l2.rename(columns={'               home_result_end':'home_result_end',
                   '               stadium':'stadium',
                   '               goal_order':'goal_order',
                   '               away_yellow':'away_yellow',}, inplace=True)
    
l3.rename(columns={'               home_result_end':'home_result_end',
                   '               stadium':'stadium',
                   '               goal_order':'goal_order',
                   '               away_yellow':'away_yellow',}, inplace=True)


########## manual corrections (StPauli vs S04) ##########
game_identifier = (l1['season'] == '2010-11') & (l1['gameday'] == 28) & (l1['home_team'] == 'St. Pauli')
l1.loc[game_identifier, 'home_result_end'] = 0
l1.loc[game_identifier, 'away_result_end'] = 2
l1.loc[game_identifier, 'home_result_break'] = 0
l1.loc[game_identifier, 'away_result_break'] = 1
# game canceled and evaluated as 0:2 (0:1)



########## append the different leagues ##########
matches = l1.append(l2)
matches = matches.append(l3)


########## drop some variables ##########
matches.drop(['away_ball', 'home_ball', 'goal_own', 'own_goals', 'grade_game', 
              'home_chances', 'away_chances', 'home_corners', 'away_corners',
              'home_shots', 'away_shots', 'sold_out'],
    axis=1, inplace=True)
matches.reset_index(inplace=True, drop=True)


# VARIABLES THAT COULD BE REACTIVATED: chances (2x), corners (2x), sold_out


########## ordering of the variables ##########
#cols = list(matches.columns.values)
matches = matches[[
        'league',
        'season',
        'gameday',
        'date',
        'weekday',
        'time',
        'home_team',
        'away_team',
        'stadium',
        'attendance',
        'home_result_end',
        'away_result_end',
        'home_result_break',
        'away_result_break',
        'goal_order',
        'goal_time',
        'goal_penalty',
        'penalties',
        'away_red',
        'away_yellow',
        'home_red',
        'home_yellow',
        'grade_ref',
        'ref_city',
        'ref_name',
        'ref_str',
        'D_delayed',
        'gameday_delayed'
        ]]




# vereinheitlichung von teamnamen
teams = matches.drop_duplicates(subset='home_team') 
teams = teams['home_team'].copy()
teams.sort_values(inplace=True)
teams.reset_index(inplace=True, drop=True)
# 68 teams in the data set

    
    


# Transfermarktdatem
l1_tm = pd.read_csv(soccer_data + 'transfermarkt_mv_age_foreigners_bl.csv', sep=';', encoding='ISO-8859-1')
l1_tm['season_first_number'] = pd.to_numeric(l1_tm['season'].str.slice(0,4))
delete_entries = l1_tm[  (l1_tm['season_first_number']<first_year_wave) | ((l1_tm['season_first_number']>last_year_wave))  ].index
l1_tm.drop(delete_entries, inplace=True)

# to do next: 
#team namen umbennenen


# Still missing data
# Tabelle
# Transfermarktdaten
# Aufsteiger, Pokalsiger und Meister






 
