# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:59:13 2019

This Program reads in the data for the matches, the table and team data. 
Each of the data sets is prepared (the prepared df are: matches, t, tm) and is 
connected together in the final df (df).


@author: Fabel
"""

#packages
import pandas as pd
import numpy as np

#paths & magic numbers
#soccer_source = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
#soccer_output = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/'

# HOME directories
soccer_source = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
soccer_output = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/'

#magic numbers
first_year_wave = 2010
last_year_wave = 2014



###############################################################################
#       1)    MATCHES
###############################################################################
#   read in all leagues from season 2010/11 untill 2014/15, 
#   generate one large file, that contains the matches across leagues


########## league 1 ##########
l1 = pd.read_csv(soccer_source + 'cross-sections/' + 'kicker_matchday_bl_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l1_temp = pd.read_csv(soccer_source + 'cross-sections/' + 'kicker_matchday_bl_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
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
l1_delayed = pd.read_csv(soccer_source + 'kicker_matchdayresults_delayedgames_bl.csv', sep=';', encoding='ISO-8859-1')
l1_delayed['season_first_number'] = pd.to_numeric(l1_delayed['season'].str.slice(0,4))
delete_entries = l1_delayed[  (l1_delayed['season_first_number']<first_year_wave) | ((l1_delayed['season_first_number']>last_year_wave))  ].index
l1_delayed.drop(delete_entries, inplace=True)
l1_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l1_delayed['D_delayed'] = 1
l1_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l1 = l1.merge(l1_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l1['D_delayed'].fillna(value=0, inplace=True)



########## league 2 ##########
l2 = pd.read_csv(soccer_source + 'cross-sections/' + 'kicker_matchday_2l_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l2_temp = pd.read_csv(soccer_source + 'cross-sections/' + 'kicker_matchday_2l_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
    l2 = l2.append(l2_temp)
l2['league']= 2
l2.reset_index(inplace=True, drop=True)

# merge delayed games
l2_delayed = pd.read_csv(soccer_source + 'kicker_matchdayresults_delayedgames_2l.csv', sep=';', encoding='ISO-8859-1')
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
l3 = pd.read_csv(soccer_source + 'kicker_matchday_3l.csv', sep=';', encoding='ISO-8859-1')
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
l3_delayed = pd.read_csv(soccer_source + 'kicker_matchdayresults_delayedgames_3l.csv', sep=';', encoding='ISO-8859-1')
l3_delayed['season_first_number'] = pd.to_numeric(l3_delayed['season'].str.slice(0,4))
delete_entries = l3_delayed[  (l3_delayed['season_first_number']<first_year_wave) | ((l3_delayed['season_first_number']>last_year_wave))  ].index
l3_delayed.drop(delete_entries, inplace=True)
l3_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l3_delayed['D_delayed'] = 1
l3_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l3 = l3.merge(l3_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l3['D_delayed'].fillna(value=0, inplace=True)


########## rename columns - remove leading blanks ##########
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


# correct team names
matches.home_team = matches.home_team.replace({
        'Bayern' 			: 'Bayern München',
        'Bayern II' 		: 'Bayern München II',
        'VfB II' 			: 'Stuttgart II',
        'Union' 			: 'Union Berlin',
        'Wehen' 			: 'Wehen Wiesbaden',
        'HSV'           : 'Hamburger SV',
        'Stuttg. Kick.' : 'Stuttgarter Kickers',
        'TSV 1860'      : '1860 München'})

matches.away_team = matches.away_team.replace({
        'Bayern' 			: 'Bayern München',
        'Bayern II' 		: 'Bayern München II',
        'VfB II' 			: 'Stuttgart II',
        'Union' 			: 'Union Berlin',
        'Wehen' 			: 'Wehen Wiesbaden',
        'HSV'           : 'Hamburger SV',
        'Stuttg. Kick.' : 'Stuttgarter Kickers',
        'TSV 1860'      : '1860 München'})


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


    
########## Stadiums ##########
# correct some stadiums
matches.stadium = matches.stadium.replace({
    'Impuls-Arena, Augsburg'                            : 'WWK-Arena, Augsburg',
    'SGL-Arena, Augsburg'                               : 'WWK-Arena, Augsburg',
    'SchÃ¼co-Arena, Bielefeld'                          : 'Schüco-Arena, Bielefeld',
    'Stadion an der GellertstraÃe, Chemnitz'           : 'Stadion an der Gellertstraße, Chemnitz',
    'StÃ¤dtisches Stadion am BÃ¶llenfalltor, Darmstadt' : 'Merck-Stadion am Böllenfalltor, Darmstadt',
    'GlÃ¼cksgas-Stadion, Dresden'                       : 'Rudolf-Harbig-Stadion, Dresden',
    'Glücksgas-Stadion, Dresden'                        : 'Rudolf-Harbig-Stadion, Dresden',
    'DDV-Stadion, Dresden'                              : 'Rudolf-Harbig-Stadion, Dresden',
    'Stadion Dresden, Dresden'                          : 'Rudolf-Harbig-Stadion, Dresden',        
    'Stadion an der Schwarzwaldstraße, Freiburg'        : 'Schwarzwald-Stadion, Freiburg',
    'Mage-Solar-Stadion, Freiburg'                      : 'Schwarzwald-Stadion, Freiburg',
    'Badenova-Stadion, Freiburg'                        : 'Schwarzwald-Stadion, Freiburg',
    'Stadion am Laubenweg, Fürth'                       : 'Sportpark Ronhof | Thomas Sommer, Fürth',
    'Trolli-Arena, Fürth'                               : 'Sportpark Ronhof | Thomas Sommer, Fürth',
    'Millerntor-Stadion, Hamburg-St. Pauli'             : 'Millerntor-Stadion, Hamburg-St.Pauli',
    'AWD-Arena, Hannover'                               : 'HDI Arena, Hannover',
    'SÃ¼dstadion, KÃ¶ln'                                : 'Südstadion, Köln',
    'Coface-Arena, Mainz'                               : 'Opel-Arena, Mainz',
    'Stadion an der GrÃ¼nwalder StraÃe, MÃ¼nchen'      : 'Stadion an der Grünwalder Straße, München',    
    'PreuÃenstadion, MÃ¼nster'                         : 'Preußenstadion, Münster',
    'Easy-Credit-Stadion, Nürnberg'                     : 'Grundig-Stadion, Nürnberg',
    'Bieberer Berg, Offenbach'                          : 'Sparda-Bank-Hessen-Stadion, Offenbach',
    'Osnatel-Arena, OsnabrÃ¼ck'                         : 'Osnatel-Arena, Osnabrück',
    'Energieteam-Arena, Paderborn'                      : 'Benteler-Arena, Paderborn',
    'StÃ¤dtisches Jahnstadion, Regensburg'              : 'Städtisches Jahnstadion, Regensburg',
    'Ludwigsparkstadion, SaarbrÃ¼cken'                  : 'Ludwigsparkstadion, Saarbrücken',
    'Rhein-Neckar-Arena, Sinsheim'                      : 'Wirsol Rhein-Neckar-Arena, Sinsheim',
    'Generali-Sportpark, Unterhaching'                  : 'Stadion am Sportpark, Unterhaching',
    'Alpenbauer Sportpark, Unterhaching'                : 'Stadion am Sportpark, Unterhaching'})    
            
    
stadiums =  matches.drop_duplicates(subset=['stadium']) # , 'home_team'
stadiums = stadiums['stadium'].copy() #, 'home_team'
stadiums.sort_values(inplace=True)    
stadiums.reset_index(inplace=True, drop=True)
stadiums = stadiums.str.split(pat=',', expand=True)
stadiums.sort_values(1, inplace=True)
stadiums = stadiums.rename(columns={0:'stadium', 1:'city'})

# 69 stadiums
# team - stadiums: 77 combinations




###############################################################################
#              2)  TABLE
###############################################################################

t1 = pd.read_csv(soccer_source +  'kicker_tablestandings_bl.csv', sep=';', encoding='ISO-8859-1')
t1['season_first_number'] = pd.to_numeric(t1['season'].str.slice(0,4))
delete_entries = t1[  (t1['season_first_number']<first_year_wave) | ((t1['season_first_number']>last_year_wave))  ].index
t1.drop(delete_entries, inplace=True)
t1.drop('season_first_number', axis=1, inplace=True)
t1['league'] = 1
t1['D_champion'] = t1['team'].str.contains('\(.*?M.*?\)').astype(int)
t1['D_winner_cup'] = t1['team'].str.contains('\(.*?P.*?\)').astype(int)
t1['D_promoted'] = t1['team'].str.contains('\(.*?N.*?\)').astype(int)

t2 = pd.read_csv(soccer_source +  'kicker_tablestandings_2l.csv', sep=';', encoding='ISO-8859-1')
t2['season_first_number'] = pd.to_numeric(t2['season'].str.slice(0,4))
delete_entries = t2[  (t2['season_first_number']<first_year_wave) | ((t2['season_first_number']>last_year_wave))  ].index
t2.drop(delete_entries, inplace=True)
t2.drop('season_first_number', axis=1, inplace=True)
t2['league'] = 2
t2['D_promoted'] = t2['team'].str.contains('\(.*?N.*?\)').astype(int)
t2['D_relegated'] = t2['team'].str.contains('\(.*?A.*?\)').astype(int)

t3 = pd.read_csv(soccer_source +  'kicker_tablestandings_3l.csv', sep=';', encoding='ISO-8859-1')
t3['season_first_number'] = pd.to_numeric(t3['season'].str.slice(0,4))
delete_entries = t3[  (t3['season_first_number']<first_year_wave) | ((t3['season_first_number']>last_year_wave))  ].index
t3.drop(delete_entries, inplace=True)
t3.drop('season_first_number', axis=1, inplace=True)
t3['league'] = 3
t3['D_promoted'] = t3['team'].str.contains('\(.*?N.*?\)').astype(int)
t3['D_relegated'] = t3['team'].str.contains('\(.*?A.*?\)').astype(int)

t = t1.append(t2)
t = t.append(t3)
t.reset_index(inplace=True, drop=True)

# reset original order
t = t[['league', 'spieltag', 'season', 'table_place', 'team', 'games', 'wins', 'draw',
       'defeats', 'goals', 'diff', 'points', 'D_champion',
       'D_winner_cup', 'D_promoted', 'D_relegated']]

t.fillna({'D_champion' : 0, 'D_winner_cup' : 0, 'D_relegated' : 0}, inplace = True)
t['D_point_deduction'] = t['team'].str.contains('.*\*').astype(int)     # * marks cases where the team obtained a point deduction from DFL
t.rename(columns={'spieltag':'gameday'}, inplace=True)

# adjust the names of the teams - make consistent
t['team'] = t['team'].str.replace('( \([^)]*\) ?\*?)|( \*)', '')


t.team = t.team.replace({
	'Alemannia Aachen' 			: 'Aachen',
	'VfR Aalen' 				: 'Aalen',
	'Rot Weiss Ahlen' 			: 'Ahlen',
	'Erzgebirge Aue' 			: 'Aue',
	'FC Augsburg' 				: 'Augsburg',
	'SV Babelsberg 03' 			: 'Babelsberg',
	'Bayern München' 			: 'Bayern München',
	'Bayern München II' 		: 'Bayern München II',
	'Arminia Bielefeld'			: 'Bielefeld',
	'VfL Bochum' 				: 'Bochum',
	'Eintracht Braunschweig' 	: 'Braunschweig',
	'Werder Bremen' 			: 'Bremen',
	'Werder Bremen II' 			: 'Bremen II',
	'Wacker Burghausen' 		: 'Burghausen',
	'Chemnitzer FC' 			: 'Chemnitz',
	'Energie Cottbus' 			: 'Cottbus',
	'SV Darmstadt 98' 			: 'Darmstadt',
	'Borussia Dortmund'			: 'Dortmund',
	'Borussia Dortmund II' 		: 'Dortmund II',
	'Dynamo Dresden' 			: 'Dresden',
	'MSV Duisburg' 				: 'Duisburg',
	'Fortuna Düsseldorf' 		: 'Düsseldorf',
	'SV Elversberg' 			: 'Elversberg',
	'Rot-Weiß Erfurt' 			: 'Erfurt',
	'FSV Frankfurt' 			: 'FSV Frankfurt',
	'Fortuna Köln' 				: 'Fortuna Köln',
	'Eintracht Frankfurt' 		: 'Frankfurt',
	'SC Freiburg' 				: 'Freiburg',
	'SpVgg Greuther Fürth' 		: 'Fürth',
	'Bor. Mönchengladbach' 		: 'Gladbach',
	'SG Sonnenhof Großaspach' 	: 'Großaspach',
	'Hamburger SV' 				: 'Hamburger SV',
	'SpVgg Unterhaching' 		: 'Haching',
	'Hallescher FC' 			: 'Halle',
	'Hannover 96' 				: 'Hannover',
	'1. FC Heidenheim' 			: 'Heidenheim',
	'Hertha BSC' 				: 'Hertha',
	'TSG Hoffenheim' 			: 'Hoffenheim',
	'FC Ingolstadt 04' 			: 'Ingolstadt',
	'Carl Zeiss Jena' 			: 'Jena',
	'1. FC Kaiserslautern'		: 'K\'lautern',
	'Karlsruher SC' 			: 'Karlsruhe',
	'Holstein Kiel' 			: 'Kiel',
	'TuS Koblenz' 				: 'Koblenz',
	'1. FC Köln' 				: 'Köln',
	'RB Leipzig' 				: 'Leipzig',
	'Bayer 04 Leverkusen' 		: 'Leverkusen',
	'1. FSV Mainz 05' 			: 'Mainz',
	'1. FSV Mainz 05 II' 		: 'Mainz II',
	'Preußen Münster' 			: 'Münster',
	'1. FC Nürnberg' 			: 'Nürnberg',
	'Rot-Weiß Oberhausen' 		: 'Oberhausen',
	'Kickers Offenbach' 		: 'Offenbach',
	'VfL Osnabrück' 			: 'Osnabrück',
	'SC Paderborn 07' 			: 'Paderborn',
	'Jahn Regensburg' 			: 'Regensburg',
	'Hansa Rostock' 			: 'Rostock',
	'1. FC Saarbrücken' 		: 'Saarbrücken',
	'SV Sandhausen' 			: 'Sandhausen',
	'FC Schalke 04' 			: 'Schalke',
	'FC St. Pauli' 				: 'St. Pauli',
	'Stuttgarter Kickers' 		: 'Stuttgarter Kickers',
	'VfB Stuttgart' 			: 'Stuttgart',
	'VfB Stuttgart II' 			: 'Stuttgart II',
	'1860 München' 				: '1860 München',
	'1. FC Union Berlin' 		: 'Union Berlin',
	'SV Wehen Wiesbaden' 		: 'Wehen Wiesbaden',
	'VfL Wolfsburg' 			: 'Wolfsburg'})

# correction of mistakes (kicker has wrong names)
t.team = t.team.replace({
	'SV Frankfurt' 			: 'FSV Frankfurt',
	'ayern München II'		: 'Bayern München II',
	'erder Bremen'			: 'Bremen',
	'intracht Frankfurt'	    : 'Frankfurt',
	'lemannia Aachen'		: 'Aachen'})






###############################################################################
#              3)  TRANSFERMARKTDATEN
###############################################################################
l1_tm = pd.read_csv(soccer_source + 'transfermarkt_mv_age_foreigners_bl.csv', sep=';', encoding='ISO-8859-1')
l1_tm['season_first_number'] = pd.to_numeric(l1_tm['season'].str.slice(0,4))
delete_entries = l1_tm[  (l1_tm['season_first_number']<first_year_wave) | ((l1_tm['season_first_number']>last_year_wave))  ].index
l1_tm.drop(delete_entries, inplace=True)
l1_tm['league'] = 1

l2_tm = pd.read_csv(soccer_source + 'transfermarkt_mv_age_foreigners_2l.csv', sep=';', encoding='ISO-8859-1')
l2_tm['season_first_number'] = pd.to_numeric(l2_tm['season'].str.slice(0,4))
delete_entries = l2_tm[  (l2_tm['season_first_number']<first_year_wave) | ((l2_tm['season_first_number']>last_year_wave))  ].index
l2_tm.drop(delete_entries, inplace=True)
l2_tm['league'] = 2

l3_tm = pd.read_csv(soccer_source + 'transfermarkt_mv_age_foreigners_3l.csv', sep=';', encoding='ISO-8859-1')
l3_tm['season_first_number'] = pd.to_numeric(l3_tm['season'].str.slice(0,4))
delete_entries = l3_tm[  (l3_tm['season_first_number']<first_year_wave) | ((l3_tm['season_first_number']>last_year_wave))  ].index
l3_tm.drop(delete_entries, inplace=True)
l3_tm['league'] = 3

tm = l1_tm.append(l2_tm)
tm = tm.append(l3_tm)
tm.drop('season_first_number', axis=1, inplace=True)

tm.team = tm.team.replace({
	'Alem. Aachen' 				: 'Aachen',
	'VfR Aalen' 				: 'Aalen',
	'Rot Weiss Ahlen' 			: 'Ahlen',
	'Erzgebirge Aue' 			: 'Aue',
	'FC Augsburg' 				: 'Augsburg',
	'Babelsberg 03' 			: 'Babelsberg',
	'Bayern München' 			: 'Bayern München',
	'B. München II' 			: 'Bayern München II',
	'Arm. Bielefeld' 			: 'Bielefeld',
	'VfL Bochum' 				: 'Bochum',
	'E. Braunschweig' 			: 'Braunschweig',
	'Werder Bremen' 			: 'Bremen',
	'Werder II' 				: 'Bremen II',
	'W. Burghausen' 			: 'Burghausen',
	'Chemnitzer FC' 			: 'Chemnitz',
	'Energie Cottbus' 			: 'Cottbus',
	'SV Darmstadt 98' 			: 'Darmstadt',
	'Bor. Dortmund' 			: 'Dortmund',
	'B. Dortmund II' 			: 'Dortmund II',
	'Dynamo Dresden' 			: 'Dresden',
	'MSV Duisburg' 				: 'Duisburg',
	'F. Düsseldorf' 			: 'Düsseldorf',
	'SV Elversberg' 			: 'Elversberg',
	'Rot-Weiß Erfurt' 			: 'Erfurt',
	'FSV Frankfurt' 			: 'FSV Frankfurt',
	'SC Fortuna Köln' 			: 'Fortuna Köln',
	'E. Frankfurt' 				: 'Frankfurt',
	'SC Freiburg' 				: 'Freiburg',
	'Greuther Fürth' 			: 'Fürth',
	'Bor. M\'gladbach' 			: 'Gladbach',
	'Sonnenhof-Gr.' 			: 'Großaspach',
	'Hamburger SV' 				: 'Hamburger SV',
	'Unterhaching' 				: 'Haching',
	'Hallescher FC' 			: 'Halle',
	'Hannover 96' 				: 'Hannover',
	'1.FC Heidenheim' 			: 'Heidenheim',
	'Hertha BSC' 				: 'Hertha',
	'TSG Hoffenheim' 			: 'Hoffenheim',
	'FC Ingolstadt' 			: 'Ingolstadt',
	'Carl Zeiss Jena' 			: 'Jena',
	'1.FC K\'lautern' 			: 'K\'lautern',
	'Karlsruher SC' 			: 'Karlsruhe',
	'Holstein Kiel' 			: 'Kiel',
	'TuS Koblenz' 				: 'Koblenz',
	'1.FC Köln' 				: 'Köln',
	'RB Leipzig' 				: 'Leipzig',
	'Bay. Leverkusen' 			: 'Leverkusen',
	'1.FSV Mainz 05' 			: 'Mainz',
	'FSV Mainz 05 II' 			: 'Mainz II',
	'Preußen Münster' 			: 'Münster',
	'1.FC Nürnberg' 			: 'Nürnberg',
	'RW Oberhausen' 			: 'Oberhausen',
	'K. Offenbach' 				: 'Offenbach',
	'VfL Osnabrück' 			: 'Osnabrück',
	'SC Paderborn' 				: 'Paderborn',
	'Jahn Regensburg' 			: 'Regensburg',
	'Hansa Rostock' 			: 'Rostock',
	'Saarbrücken' 				: 'Saarbrücken',
	'SV Sandhausen' 			: 'Sandhausen',
	'FC Schalke 04' 			: 'Schalke',
	'FC St. Pauli' 				: 'St. Pauli',
	'Stuttg. Kickers' 			: 'Stuttgarter Kickers',
	'VfB Stuttgart' 			: 'Stuttgart',
	'Stuttgart II' 				: 'Stuttgart II',
	'1860 München' 				: '1860 München',
	'Union Berlin' 				: 'Union Berlin',
	'Wehen Wiesbaden' 			: 'Wehen Wiesbaden',
	'VfL Wolfsburg' 			: 'Wolfsburg'})

tm.rename(columns={'size' : 'team_size',
                   'average_age' : 'team_average_age',
                   'foreigners' : 'team_foreigners',
                   'market_value' : 'team_market_value'}, inplace=True)









###############################################################################
#       4) COMBINE ALL PREPARED DATA -> FINAL DF
###############################################################################

#   merge matches to table, for home and away team seperately, remove games 
#    where there's no information. In the end append the two data sets
    
    
########## Home team ##########
matches_ht = matches.copy()
matches_ht.rename(columns={
        'home_team'         : 'team',
        'away_team'         : 'opp_team',
        'home_result_end'   : 'own_result_end',
        'away_result_end'   : 'opp_result_end',
        'home_result_break' : 'own_result_break',
        'away_result_break' : 'opp_result_break',
        'away_red'          : 'opp_red',
        'away_yellow'       : 'opp_yellow',
        'home_red'          : 'own_red',
        'home_yellow'       : 'own_yellow'}, inplace=True)
df_ht = t.merge(matches_ht, on=['league','season','gameday', 'team'], how='outer', indicator=True)
df_ht['D_home_game'] = df_ht['_merge'].str.contains('both', regex=False).astype(int)
df_ht.drop('_merge', axis=1, inplace=True)

# drop unmatched (away) teams
away_teams = df_ht[ (df_ht['D_home_game'] == 0)].index
df_ht.drop(away_teams, inplace=True)



########## Away Team ##########
matches_at = matches.copy()
matches_at.rename(columns={
        'home_team'         : 'opp_team',
        'away_team'         : 'team',
		'home_result_end'   : 'opp_result_end',
        'away_result_end'   : 'own_result_end',
        'home_result_break' : 'opp_result_break',
        'away_result_break' : 'own_result_break',
        'away_red'          : 'own_red',
        'away_yellow'       : 'own_yellow',
        'home_red'          : 'opp_red',
        'home_yellow'       : 'opp_yellow'}, inplace=True)

# Reverse the score (change perspective to the away team)    
def reverse_score(score):
    if score is not None:
        if score is not np.nan: 
            L = score.split(':')
            S = str(L[1]) + ":" + str(L[0])
        else: 
            S = np.nan
    else:
        S = None
    return S

goal_order_at = matches_at['goal_order']    
goal_order_at = goal_order_at.str.split(pat='/', expand=True)
list_number_goals_in_game = []    # needed to concetenate columns
for column in range(0, len(goal_order_at.columns)):
    goal_order_at[column] = goal_order_at[column].apply(reverse_score)
    goal_order_at[column] = goal_order_at[column].fillna('')
    list_number_goals_in_game.append(column)

# put together again 
goal_order_at['reversed'] = goal_order_at[list_number_goals_in_game].apply(
        lambda row: '/'.join(row.values.astype(str)), axis=1)
goal_order_at['reversed'] = goal_order_at['reversed'].str.rstrip('/')
goal_order_at.reversed = goal_order_at.reversed.replace({'': np.nan})
matches_at['goal_order'] = goal_order_at['reversed']

# merge macthes to table
df_at = t.merge(matches_at, on=['league','season','gameday', 'team'], how='outer', indicator=True)
df_at['D_away_game'] = df_at['_merge'].str.contains('both', regex=False).astype(int)
df_at.drop('_merge', axis=1, inplace=True)
# drop unmatched (home) teams
home_teams = df_at[ (df_at['D_away_game'] == 0)].index
df_at.drop(home_teams, inplace=True)
df_at.drop('D_away_game', axis=1, inplace=True)


# append home and away data frame
df = df_ht.append(df_at)
df['D_home_game'].fillna(value=0, inplace=True)

# encode some of the columns
df['own_result_end'] = pd.to_numeric(df['own_result_end'], errors='ignore')
df['opp_result_end'] = pd.to_numeric(df['opp_result_end'], errors='ignore')

df['grade_ref'] = df['grade_ref'].str.replace(',', '.')
df['grade_ref'] = pd.to_numeric(df['grade_ref'], errors='ignore')




########## Transfermakrtdaten ##########
df = df.merge(tm, on=['season', 'team', 'league'], how='outer')
#encode variables
for var in ['team_average_age', 'team_market_value']: 
    df[var] = df[var].str.replace(',', '.')
    df[var] = pd.to_numeric(df[var], errors='ignore')
    
    
    

########## Sort & Order ##########
df = 	df[[
    'league', 'season', 'gameday', 
	'table_place', 'points', 'team', 
	'opp_team', 'D_home_game', 'date', 'weekday', 'time', 
	'stadium', 'attendance', 'own_result_end', 'opp_result_end',
    'own_result_break', 'opp_result_break', 'goal_order', 'goal_time',
    'goal_penalty', 'penalties', 'opp_red', 'opp_yellow', 'own_red',
    'own_yellow', 'grade_ref', 'ref_city', 'ref_name', 'ref_str',
    'D_delayed', 'gameday_delayed', 
	'games', 'wins', 'draw', 'defeats', 'goals', 'diff',
	'D_champion', 'D_winner_cup', 'D_promoted', 'D_relegated', 'D_point_deduction',
    'team_size', 'team_average_age', 'team_foreigners', 'team_market_value']]
df.sort_values(['league','season','gameday','table_place'], inplace=True)
df.reset_index(inplace=True, drop=True)


# read out
df.to_csv(soccer_output + 'soccer_prepared.csv', sep=';')

###############################################################################
#           END OF FILE
###############################################################################




# Comments:
#   - für mehr jahre siehe korrekturen v Dominik
#   - fürth Stadion name was changed; is a match possible? ('|')
#   - match for osnabrück possible or did Dominik use the Bremer Brücke?
#   - Mainz: Bruchweg Stadion: Dominik changed it erroneously to Opel Arena
#       -> coordinates might be missing



# TO DO:
#   1) some variables are float that should be int, e.g D_delayed
#   2) pregamepoint difference
#   3) merge to stadiums df geographic information collected by Dominik





