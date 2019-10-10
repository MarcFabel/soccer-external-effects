# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:59:13 2019

@author: Fabel


Descritpion:
     This Program reads in the data for the matches, the table and team data.
     Each of the data sets is prepared (the prepared df are: matches, t, tm) and is
     connected together in the final df (df).


Inputs:
     - kicker_matchday_XL_XXXX.csv           source    cross-section of matches, obtained via kicker.de (webscraping)
     - stadiums_coordinates_1011_1617.xlsx   source    geographic features (GPS coordinates, adress - set up manually)
     - kicker_tablestandings_Xl.csv          source    contains the table standings for the 3 leagues
     -transfermarkt_mv_age_foreigners_Xl.csv source    contains transfermarktdata for all leagues

Outputs:
     - stadiums_geographic_information.csv   intermed  contains geographic components for the stadiums in our sample, is used by QGIS
     - soccer_prepared_table_based.csv       intermed  prepared df, on the level of each team, handy when there is a definition of active regions including away games
     - soccer_prepared.csv                   final     final df, on the level of the match - useful when only home games activate a region

"""

# packages
import pandas as pd
import numpy as np
import time
start_time = time.time()


# paths
z_soccer_webscraping_source   = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
z_soccer_source               = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/'
z_soccer_output_intermediate  = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/soccer/'
z_soccer_output_final         = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'


# HOME directories
#z_soccer_webscraping_source = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
#z_soccer_source  = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/'
#z_soccer_output_intermediate = '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/soccer/'


# magic numbers
first_year_wave = 2010
last_year_wave = 2014



###############################################################################
#       1)    MATCHES
###############################################################################
#   read in all leagues from season 2010/11 untill 2014/15,
#   generate one large file, that contains the matches across leagues


########## league 1 ##########
l1 = pd.read_csv(z_soccer_webscraping_source + 'cross-sections/' + 'kicker_matchday_bl_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l1_temp = pd.read_csv(z_soccer_webscraping_source + 'cross-sections/' + 'kicker_matchday_bl_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
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
l1_delayed = pd.read_csv(z_soccer_webscraping_source + 'kicker_matchdayresults_delayedgames_bl.csv', sep=';', encoding='ISO-8859-1')
l1_delayed['season_first_number'] = pd.to_numeric(l1_delayed['season'].str.slice(0,4))
delete_entries = l1_delayed[  (l1_delayed['season_first_number']<first_year_wave) | ((l1_delayed['season_first_number']>last_year_wave))  ].index
l1_delayed.drop(delete_entries, inplace=True)
l1_delayed.drop(['season_first_number','result_end', 'result_break'], axis=1, inplace=True)
l1_delayed['D_delayed'] = 1
l1_delayed.rename(columns={'spieltag_nachgeholt':'gameday_delayed'}, inplace=True)
l1 = l1.merge(l1_delayed, on=['season', 'weekday', 'date', 'time', 'home_team', 'away_team'], how='outer')
l1['D_delayed'].fillna(value=0, inplace=True)



########## league 2 ##########
l2 = pd.read_csv(z_soccer_webscraping_source + 'cross-sections/' + 'kicker_matchday_2l_' + str(first_year_wave) + '.csv', sep=';', encoding='ISO-8859-1')
for item in range(first_year_wave+1, last_year_wave+1):
    l2_temp = pd.read_csv(z_soccer_webscraping_source + 'cross-sections/' + 'kicker_matchday_2l_{}.csv'.format(item), sep=';', encoding='ISO-8859-1')
    l2 = l2.append(l2_temp)
l2['league']= 2
l2.reset_index(inplace=True, drop=True)

# merge delayed games
l2_delayed = pd.read_csv(z_soccer_webscraping_source + 'kicker_matchdayresults_delayedgames_2l.csv', sep=';', encoding='ISO-8859-1')
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
l3 = pd.read_csv(z_soccer_webscraping_source + 'kicker_matchday_3l.csv', sep=';', encoding='ISO-8859-1')
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
l3_delayed = pd.read_csv(z_soccer_webscraping_source + 'kicker_matchdayresults_delayedgames_3l.csv', sep=';', encoding='ISO-8859-1')
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


########## manual corrections  ##########
# StPauli vs S04 - game canceled and evaluated as 0:2 (0:1)
game_identifier = (l1['season'] == '2010-11') & (l1['gameday'] == 28) & (l1['home_team'] == 'St. Pauli')
l1.loc[game_identifier, 'home_result_end'] = 0
l1.loc[game_identifier, 'away_result_end'] = 2
l1.loc[game_identifier, 'home_result_break'] = 0
l1.loc[game_identifier, 'away_result_break'] = 1

# corrections for attendance (matches played behind closed doors)
game_identifier = (l2['season'] == '2011-12') & (l2['gameday'] == 19) & (l2['home_team'] == 'Rostock')
l2.loc[game_identifier, 'attendance'] = 0   # Zuschauerausschluss
l2.loc[game_identifier, 'sold_out'] = 0

game_identifier = (l2['season'] == '2011-12') & (l2['gameday'] == 25) & (l2['home_team'] == 'Dresden')
l2.loc[game_identifier, 'attendance'] = 0   # Zuschauerausschluss
l2.loc[game_identifier, 'sold_out'] = 0

game_identifier = (l3['season'] == '2012-13') & (l3['gameday'] == 4) & (l3['home_team'] == 'Karlsruhe')
l3.loc[game_identifier, 'attendance'] = 0   # Zuschauerausschluss
l3.loc[game_identifier, 'sold_out'] = 0

game_identifier = (l3['season'] == '2014-15') & (l3['gameday'] == 24) & (l3['home_team'] == 'Dresden')
l3.loc[game_identifier, 'attendance'] = 0   # Zuschauerausschluss
l3.loc[game_identifier, 'sold_out'] = 0




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
    'Scholz-Arena, Aalen'                               : 'Ostalb Arena, Aalen',
    'Sparkassen-Erzgebirgsstadion, Aue'                 : 'Erzgebirgsstadion, Aue',
    'SchÃ¼co-Arena, Bielefeld'                          : 'Schüco-Arena, Bielefeld',
    'Rewirpower-Stadion, Bochum'                        : 'Vonovia-Ruhrstadion, Bochum',
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
    'Imtech-Arena, Hamburg'                             : 'Volksparkstadion, Hamburg',
    'Millerntor-Stadion, Hamburg-St. Pauli'             : 'Millerntor-Stadion, Hamburg-St.Pauli',
    'AWD-Arena, Hannover'                               : 'HDI Arena, Hannover',
    'SÃ¼dstadion, KÃ¶ln'                                : 'Südstadion, Köln',
    'Coface-Arena, Mainz'                               : 'Opel-Arena, Mainz',
    'Stadion an der GrÃ¼nwalder StraÃe, MÃ¼nchen'      : 'Stadion an der Grünwalder Straße, München',
    'PreuÃenstadion, MÃ¼nster'                         : 'Preußenstadion, Münster',
    'Easy-Credit-Stadion, Nürnberg'                     : 'Grundig-Stadion, Nürnberg',
    'Bieberer Berg, Offenbach'                          : 'Sparda-Bank-Hessen-Stadion, Offenbach',
    'Osnatel-Arena, OsnabrÃ¼ck'                         : 'Bremer Brücke, Osnabrück',
    'Osnatel-Arena, Osnabrück'                          : 'Bremer Brücke, Osnabrück',
    'Energieteam-Arena, Paderborn'                      : 'Benteler-Arena, Paderborn',
    'StÃ¤dtisches Jahnstadion, Regensburg'              : 'Städtisches Jahnstadion, Regensburg',
    'DKB-Arena, Rostock'                                : 'Ostseestadion, Rostock',
    'Ludwigsparkstadion, SaarbrÃ¼cken'                  : 'Ludwigsparkstadion, Saarbrücken',
    'Hardtwaldstadion, Sandhausen'                      : 'BWT-Stadion am Hardtwald, Sandhausen',
    'Rhein-Neckar-Arena, Sinsheim'                      : 'Wirsol Rhein-Neckar-Arena, Sinsheim',
    'Generali-Sportpark, Unterhaching'                  : 'Stadion am Sportpark, Unterhaching',
    'Alpenbauer Sportpark, Unterhaching'                : 'Stadion am Sportpark, Unterhaching'})


# drop duplicates
stadiums =  matches.drop_duplicates(subset=['stadium']) # , 'home_team'
stadiums = stadiums['stadium'].copy() #, 'home_team'
#stadiums = stadiums.str.split(pat=',', expand=True)
#stadiums.sort_values(1, inplace=True)
#stadiums = stadiums.rename(columns={0:'stadium', 1:'city'})
stadiums = stadiums.to_frame()
len_stadiums = len(stadiums)

# 69 stadiums, w/o the weird stadiums: 65
# team - stadiums: 77 combinations


# add Geographic components (intern Domink set up the data base)
stadiums_geo = pd.read_excel(z_soccer_source  + 'stadiums_coordinates_1011_1617.xlsx')
stadiums = stadiums.merge(stadiums_geo, on=['stadium'], how='outer', indicator=True)
stadiums.sort_values(['Ort'], inplace=True)
drop_rows = stadiums[stadiums['_merge'] != 'both'].index
stadiums.drop(drop_rows, inplace=True)
assert(len(stadiums) == len_stadiums)
stadiums.drop('_merge', inplace=True, axis=1)

#count number of matches played in the single stadiums
number_matches_stadium = matches['stadium'].value_counts().to_frame()
number_matches_stadium.reset_index(inplace=True)
number_matches_stadium.rename(columns={
        'index':'stadium', 'stadium':'games_played'}, inplace =True)
stadiums = stadiums.merge(number_matches_stadium, on='stadium', how='inner')


# drop stadiums which are used only sporadically (i.e. less than a season)
#stadiums['drop'] = np.where(stadiums.games_played < 17, 1, 0)
#drop_stadiums =  stadiums.loc[stadiums['drop']==1][['stadium', 'drop']]
#stadiums.drop( stadiums[stadiums['drop']==1].index, inplace=True)
#stadiums.drop('drop', axis=1, inplace=True)


# write out for QGIS:
stadiums.sort_values(by='Ort', inplace=True)
stadiums.reset_index(inplace=True, drop=True)
stadiums.to_csv(z_soccer_output_intermediate + 'stadiums_geographic_information.csv', sep=';')


# delete 30 matches which are taking place in arenas where there are usually no games (see two blocks above)
#matches = matches.merge(drop_stadiums, on=['stadium'], how='outer')
#matches.drop( matches[matches['drop']==1].index, inplace=True)




###############################################################################
#              2)  TABLE
###############################################################################

t1 = pd.read_csv(z_soccer_webscraping_source +  'kicker_tablestandings_bl.csv', sep=';', encoding='ISO-8859-1')
t1['season_first_number'] = pd.to_numeric(t1['season'].str.slice(0,4))
delete_entries = t1[  (t1['season_first_number']<first_year_wave) | ((t1['season_first_number']>last_year_wave))  ].index
t1.drop(delete_entries, inplace=True)
t1.drop('season_first_number', axis=1, inplace=True)
t1['league'] = 1
t1['D_champion'] = t1['team'].str.contains('\(.*?M.*?\)').astype(int)
t1['D_winner_cup'] = t1['team'].str.contains('\(.*?P.*?\)').astype(int)
t1['D_promoted'] = t1['team'].str.contains('\(.*?N.*?\)').astype(int)

t2 = pd.read_csv(z_soccer_webscraping_source +  'kicker_tablestandings_2l.csv', sep=';', encoding='ISO-8859-1')
t2['season_first_number'] = pd.to_numeric(t2['season'].str.slice(0,4))
delete_entries = t2[  (t2['season_first_number']<first_year_wave) | ((t2['season_first_number']>last_year_wave))  ].index
t2.drop(delete_entries, inplace=True)
t2.drop('season_first_number', axis=1, inplace=True)
t2['league'] = 2
t2['D_promoted'] = t2['team'].str.contains('\(.*?N.*?\)').astype(int)
t2['D_relegated'] = t2['team'].str.contains('\(.*?A.*?\)').astype(int)

t3 = pd.read_csv(z_soccer_webscraping_source +  'kicker_tablestandings_3l.csv', sep=';', encoding='ISO-8859-1')
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
l1_tm = pd.read_csv(z_soccer_webscraping_source + 'transfermarkt_mv_age_foreigners_bl.csv', sep=';', encoding='ISO-8859-1')
l1_tm['season_first_number'] = pd.to_numeric(l1_tm['season'].str.slice(0,4))
delete_entries = l1_tm[  (l1_tm['season_first_number']<first_year_wave) | ((l1_tm['season_first_number']>last_year_wave))  ].index
l1_tm.drop(delete_entries, inplace=True)
l1_tm['league'] = 1

l2_tm = pd.read_csv(z_soccer_webscraping_source + 'transfermarkt_mv_age_foreigners_2l.csv', sep=';', encoding='ISO-8859-1')
l2_tm['season_first_number'] = pd.to_numeric(l2_tm['season'].str.slice(0,4))
delete_entries = l2_tm[  (l2_tm['season_first_number']<first_year_wave) | ((l2_tm['season_first_number']>last_year_wave))  ].index
l2_tm.drop(delete_entries, inplace=True)
l2_tm['league'] = 2

l3_tm = pd.read_csv(z_soccer_webscraping_source + 'transfermarkt_mv_age_foreigners_3l.csv', sep=';', encoding='ISO-8859-1')
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
#       4) COMBINE ALL PREPARED DATA & CREATE VARIABLES  -> FINAL DF BASED ON POSITION IN TABLE
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




########## Transfermarktdaten ##########
df = df.merge(tm, on=['season', 'team', 'league'], how='outer')
#encode variables
for var in ['team_average_age', 'team_market_value']:
    df[var] = df[var].str.replace(',', '.')
    df[var] = pd.to_numeric(df[var], errors='ignore')



########## Pregame point difference ##########
# subset of columns, set gameday number forward by one day
pgpd = df[['league', 'season', 'gameday', 'points', 'team']].copy()
pgpd['gameday'] += 1
pgpd.rename(columns={'points':'points_last_gameday'}, inplace=True)

# merge to data frame
df = df.merge(pgpd, on=['league','season','gameday', 'team'], how='left', indicator=False)
df['points_last_gameday'].fillna(value=0, inplace=True)
df.rename(columns={'points_last_gameday':'points_last_gameday_own'}, inplace = True)

pgpd.rename(columns={'team':'opp_team'}, inplace=True)
df = df.merge(pgpd, on=['league','season','gameday', 'opp_team'], how='left', indicator=False)
df['points_last_gameday'].fillna(value=0, inplace=True)
df.rename(columns={'points_last_gameday':'points_last_gameday_opp'}, inplace = True)

df['pregame_point_diff']= df['points_last_gameday_own'] - df['points_last_gameday_opp']
df.drop(['points_last_gameday_own', 'points_last_gameday_opp'], axis=1, inplace=True)



########## Sort & Order ##########
df = 	df[[
    'league', 'season', 'gameday',
	'table_place', 'points', 'team',
	'opp_team', 'pregame_point_diff', 'D_home_game', 'date', 'weekday', 'time',
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


# correct dtypes
col_float_to_int = [
	'pregame_point_diff',
	'D_home_game',
	'attendance',
	'own_result_end',
	'opp_result_end',
	'own_result_break',
	'opp_result_break',
	'penalties',
	'opp_red',
	'opp_yellow',
	'own_red',
	'own_yellow',
	'D_delayed',
	'D_champion',
	'D_winner_cup',
	'D_relegated'] # gameday_delayed taken out, as nan cannot be converted to int
df[col_float_to_int] = df[col_float_to_int].astype(int)


# read out
df.to_csv(z_soccer_output_intermediate + 'soccer_prepared_table_based.csv', sep=';', encoding='UTF-8', index=False)




###############################################################################
#       5) FINAL DF MATCH BASED - FOCUC ON HOME TEAM (stadium->active AGS)
###############################################################################


########## merge the table standings to the matches ##########
soccer = matches.copy()

# home team
t_ht = t.copy()
t_ht.rename(columns={
	'team'						: 'home_team',
	'table_place'				: 'home_table_place',
	'games'						: 'home_games',
	'wins'						: 'home_wins',
	'draw'						: 'home_draw',
	'defeats'					: 'home_defeats',
	'goals'						: 'home_goals',
	'diff'						: 'home_diff',
	'points'					: 'home_points',
	'D_champion'				: 'home_D_champion',
	'D_winner_cup'				: 'home_D_winner_cup',
	'D_promoted'	            : 'home_D_promoted',
    'D_relegated'               : 'home_D_relegated',
	'D_point_deduction'			: 'home_D_point_deduction'}, inplace=True)

#away team
t_at = t.copy()
t_at.rename(columns={
	'team'						: 'away_team',
	'table_place'				: 'away_table_place',
	'games'						: 'away_games',
	'wins'						: 'away_wins',
	'draw'						: 'away_draw',
	'defeats'					: 'away_defeats',
	'goals'						: 'away_goals',
	'diff'						: 'away_diff',
	'points'					: 'away_points',
	'D_champion'				: 'away_D_champion',
	'D_winner_cup'				: 'away_D_winner_cup',
	'D_promoted'            	: 'away_D_promoted',
    'D_relegated'               : 'away_D_relegated',
	'D_point_deduction'			: 'away_D_point_deduction'}, inplace=True)


soccer = soccer.merge(t_ht, on=['league','season','gameday','home_team'])
soccer = soccer.merge(t_at, on=['league','season','gameday','away_team'])



########## merge Transfermarktdaten ##########
tm_ht = tm.copy()
tm_ht.rename(columns={
	'team'				: 'home_team',
	'team_size'			: 'home_team_size',
	'team_average_age'	: 'home_team_average_age',
	'team_foreigners'	: 'home_team_foreigners',
	'team_market_value'	: 'home_team_market_value'}, inplace=True)
tm_at = tm.copy()
tm_at.rename(columns={
	'team'				: 'away_team',
	'team_size'			: 'away_team_size',
	'team_average_age'	: 'away_team_average_age',
	'team_foreigners'	: 'away_team_foreigners',
	'team_market_value'	: 'away_team_market_value'}, inplace=True)

soccer = soccer.merge(tm_ht, on=['league', 'season', 'home_team'])
soccer = soccer.merge(tm_at, on=['league', 'season', 'away_team'])



########## ENCODE variables ##########
# generate floats
for var in ['grade_ref', 'home_team_average_age', 'home_team_market_value', 'away_team_average_age', 'away_team_market_value']:
     soccer[var] = soccer[var].str.replace(',', '.')
     soccer[var] = pd.to_numeric(soccer[var])



# date variable
soccer['date'] = pd.to_datetime(soccer['date'], format='%d.%m.%Y')



########## GENERATE variables ##########

# pre-game point difference
# subset of columns, set gameday number forward by one day
pgpd = t[['league', 'season', 'gameday', 'points', 'team']].copy()
pgpd['gameday'] += 1
pgpd.rename(columns={'points':'points_last_gameday'}, inplace=True)
# merge pts last game to home team
pgpd.rename(columns={'team':'home_team'},inplace=True)
soccer = soccer.merge(pgpd, on=['league','season','gameday', 'home_team'], how='left')
soccer['points_last_gameday'].fillna(value=0, inplace=True)
soccer.rename(columns={'points_last_gameday':'home_points_last_gameday'}, inplace=True)
# merge pts last game to away team
pgpd.rename(columns={'home_team':'away_team'},inplace=True)
soccer = soccer.merge(pgpd, on=['league','season','gameday', 'away_team'], how='left')
soccer['points_last_gameday'].fillna(value=0, inplace=True)
soccer.rename(columns={'points_last_gameday':'away_points_last_gameday'}, inplace=True)
# generate pregame point spread
soccer['pregame_point_diff']= (soccer['home_points_last_gameday'] - soccer['away_points_last_gameday']).astype(int)
soccer.drop(['home_points_last_gameday', 'away_points_last_gameday'], axis=1, inplace=True)



########## SORT & ORDER ##########
soccer = 	soccer[[
    'league', 'season', 'gameday',
	'home_team', 'away_team', 'pregame_point_diff',
	'date', 'weekday', 'time',
	'stadium', 'attendance', 'home_result_end', 'away_result_end',
    'home_result_break', 'away_result_break', 'goal_order', 'goal_time',
    'goal_penalty', 'penalties', 'away_red', 'away_yellow', 'home_red',
    'home_yellow', 'grade_ref', 'ref_city', 'ref_name', 'ref_str',
    'D_delayed', 'gameday_delayed',
	'home_table_place','home_games','home_wins','home_draw','home_defeats','home_goals','home_diff','home_points','home_D_champion','home_D_winner_cup','home_D_promoted','home_D_relegated','home_D_point_deduction',
	'away_table_place','away_games','away_wins','away_draw','away_defeats','away_goals','away_diff','away_points','away_D_champion','away_D_winner_cup','away_D_promoted','away_D_relegated','away_D_point_deduction',
	'home_team_size','home_team_average_age','home_team_foreigners','home_team_market_value',
	'away_team_size','away_team_average_age','away_team_foreigners','away_team_market_value'
]]
soccer.sort_values(['league','season','gameday','date', 'time', 'home_table_place'], inplace=True)
soccer.reset_index(inplace=True, drop=True)


# corret dtypes
# correct dtypes
col_float_to_int = [
	'pregame_point_diff',
	'attendance',
	'home_result_end',
	'away_result_end',
	'home_result_break',
	'away_result_break',
	'penalties',
	'D_delayed',
	'away_red',
	'away_yellow',
	'home_red',
	'home_yellow',
	'home_D_champion',
	'home_D_winner_cup',
	'home_D_relegated',
	'away_D_champion',
	'away_D_winner_cup',
	'away_D_relegated'
] # gameday_delayed taken out, as nan cannot be converted to int
soccer[col_float_to_int] = soccer[col_float_to_int].astype(int)


# read out
soccer.to_csv(z_soccer_output_final + 'soccer_prepared.csv', sep=';', encoding='UTF-8', index=False)

###############################################################################
#           END OF FILE
###############################################################################
print("--- %s seconds ---" % (time.time() - start_time))



# TO DO:
#   - control geographic information collecetd by Dominik
#   - drop games that take place in weird locations: e.g. at Lohmühle Lübeck, Airberlin Düsseldorf, others?
#       * => check in stadiums df: there is a column with the number of games played in that location
#       * # drop special game between St Pauli vs. Ingolstadt that took place in Lübeck:
#         drop_game = l2[ (l2['season'] == '2011-12') & (l2['gameday'] == 1) & (l2['home_team'] == 'St. Pauli')].index
#         l2.drop(drop_game, inplace=True)




# Comments:
#   - juts focus on games with
#   - more years of correction of stadiums (in case the window of games is enlarged):

#Daten$stadium[Daten$stadium == "Allianz-Arena, MÃ¼nchen"] <- "Allianz-Arena, München"
#Daten$stadium[Daten$stadium == "Rhein-Energie-Stadion, KÃ¶ln"] <- "Rhein-Energie-Stadion, Köln"
#Daten$stadium[Daten$stadium == "Borussia-Park, MÃ¶nchengladbach"] <- "Borussia-Park, Mönchengladbach"
#Daten$stadium[Daten$stadium == "LTU-Arena, DÃ¼sseldorf"] <- "LTU-Arena, Düsseldorf"
#Daten$stadium[Daten$stadium == "Merck-Stadion am BÃ¶llenfalltor, Darmstadt"] <- "Merck-Stadion am Böllenfalltor, Darmstadt"
#
#Daten$stadium[Daten$stadium == "Jonathan-Heimes-Stadion am Böllenfalltor, Darmstadt"] <- "Merck-Stadion am Böllenfalltor, Darmstadt"
#Daten$stadium[Daten$stadium == "Flyeralarm-Arena, WÃ¼rzburg"] <- "Flyeralarm-Arena, Würzburg"
#Daten$stadium[Daten$stadium == "Bremer BrÃ¼cke, OsnabrÃ¼ck"] <- "Bremer Brücke, Osnabrück"
#Daten$stadium[Daten$stadium == "HÃ¤nsch-Arena, Meppen"] <- "Hänsch-Arena, Meppen"
#Daten$stadium[Daten$stadium == "Bruchwegstadion, Mainz"] <- "Opel-Arena, Mainz"
#Daten$stadium[Daten$stadium == "Hardtwaldstadion, Sandhausen"] <- "BWT-Stadion am Hardtwald, Sandhausen"
#Daten$stadium[Daten$stadium == "Community4you-Arena, Chemnitz"] <- "Stadion an der Gellertstraße, Chemnitz"
#Daten$stadium[Daten$stadium == "Gagfah-Arena, Heidenheim"] <- "Voith-Arena, Heidenheim"
#Daten$stadium[Daten$stadium == "Gottlieb-Daimler Stadion, Stuttgart"] <- "Mercedes-Benz-Arena, Stuttgart"
#Daten$stadium[Daten$stadium == "LTU-Arena, Düsseldorf"] <- "Esprit-Arena, Düsseldorf"
#Daten$stadium[Daten$stadium == "Paragon-Arena, Paderborn"] <- "Benteler-Arena, Paderborn"
#Daten$stadium[Daten$stadium == "Stadion Dresden, Dresden"] <- "Rudolf-Harbig-Stadion, Dresden"
#Daten$stadium[Daten$stadium == "Stadion Nürnberg, Nürnberg"] <- "Grundig-Stadion, Nürnberg"

#   - merge to stadiums df geographic information collected by Dominik





