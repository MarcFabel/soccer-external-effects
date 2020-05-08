#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:13:03 2020

@author: marcfabel


Descritpion:
     This file scrapes and prepares data on odds from oddsportal.com


Inputs:
     - oddsportal_lX.csv                     source         the scraped data, which was edited manually in order to account for some minor mistakes


Outputs:
     - oddsportal_prepared.csv               final          final prepared data set
     - oddsportal_lX.csv                     source         the scraped data, see above (also used as input)



"""

#packages
import re
from selenium import webdriver 
import pandas as pd


# paths HOME
z_bets_output_src =            '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
z_bets_input_src =             '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/soccer/webscraping/output/'
z_bets_output_final =          '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_prefix =                     'soc_ext_'





###############################################################################
#       1)    Scraping
###############################################################################



##########  BundesligaLiga   ##################################################

# empty data
data =str()

for season in range(2010,2015): # 2010,2015
	for page_counter in range(1,8): # 1,8
	
		link = 'https://www.oddsportal.com/soccer/germany/bundesliga-\
'+str(season) + '-' + str(season + 1)+'/results/#/page/' + str(page_counter) +'/'
		
		
		# chrome incognito
		option = webdriver.ChromeOptions()
		option.add_argument(' — incognito')
		
		# new instance of chrome
		browser = webdriver.Chrome(executable_path='/Users/marcfabel/Downloads/chromedriver',
                             options=option)
		browser.get(link)
		
		
		# get page element as string: 
		titles_element = browser.find_elements_by_xpath("//table[@class=' table-main']")	
		table = titles_element[0].text
		
		
		# delete head (first five rows)
		table_list = table.split("\n")[5:]
		table_str_delim = ';'.join(table_list)
		
		# split with Uhrzeit and date
		table_str_final = re.sub(r'([0-9]{2}:[0-9]{2})', r'\n;\1;', table_str_delim)
		table_str_final = re.sub(r'([0-9]{2} [A-Z][a-z]{2} [0-9]{4})', r'\n\1', table_str_final)
		
		# add delim before result
		table_str_final = re.sub(r'([0-9]:[0-9];)', r';\1', table_str_final)
		
		# remove last delim per line
		table_str_final = table_str_final.replace(";6;\n", ";6\n")
		table_str_final = table_str_final.replace(" 1 X 2 B's;\n", ";;;;;;;\n")
	
		browser.close()
		
		# append data
		data = data + table_str_final


df_l1 = pd.DataFrame([x.split(';') for x in data.split('\n')])




##########  2. Liga   #########################################################

# empty data
data =str()

for season in range(2010,2015): # 2010,2015
	for page_counter in range(1,8): # 1,8
	
		link = 'https://www.oddsportal.com/soccer/germany/2-bundesliga-\
'+str(season) + '-' + str(season + 1)+'/results/#/page/' + str(page_counter) +'/'
		
		
		# chrome incognito
		option = webdriver.ChromeOptions()
		option.add_argument(' — incognito')
		
		# new instance of chrome
		browser = webdriver.Chrome(executable_path='/Users/marcfabel/Downloads/chromedriver',
                             options=option)
		browser.get(link)
		
		
		# get page element as string: 
		titles_element = browser.find_elements_by_xpath("//table[@class=' table-main']")	
		table = titles_element[0].text
		
		
		# delete head (first five rows)
		table_list = table.split("\n")[5:]
		table_str_delim = ';'.join(table_list)
		
		# split with Uhrzeit and date
		table_str_final = re.sub(r'([0-9]{2}:[0-9]{2})', r'\n;\1;', table_str_delim)
		table_str_final = re.sub(r'([0-9]{2} [A-Z][a-z]{2} [0-9]{4})', r'\n\1', table_str_final)
		
		# add delim before result
		table_str_final = re.sub(r'([0-9]:[0-9];)', r';\1', table_str_final)
		
		# remove last delim per line
		table_str_final = table_str_final.replace(";6;\n", ";6\n")
		table_str_final = table_str_final.replace(" 1 X 2 B's;\n", ";;;;;;;\n")
	
		browser.close()
		
		# append data
		data = data + table_str_final

df_l2 = pd.DataFrame([x.split(';') for x in data.split('\n')])






##########  3. Liga   #########################################################

# empty data
data =str()

for season in range(2010,2015): # 2010,2015
	for page_counter in range(1,9): # 1,8
	
		link = 'https://www.oddsportal.com/soccer/germany/3-liga-\
'+str(season) + '-' + str(season + 1)+'/results/#/page/' + str(page_counter) +'/'
		
		
		# chrome incognito
		option = webdriver.ChromeOptions()
		option.add_argument(' — incognito')
		
		# new instance of chrome
		browser = webdriver.Chrome(executable_path='/Users/marcfabel/Downloads/chromedriver', 
                             options=option)
		browser.get(link)
		
		
		# get page element as string: 
		titles_element = browser.find_elements_by_xpath("//table[@class=' table-main']")	
		table = titles_element[0].text
		
		
		# delete head (first five rows)
		table_list = table.split("\n")[5:]
		table_str_delim = ';'.join(table_list)
		
		# split with Uhrzeit and date
		table_str_final = re.sub(r'([0-9]{2}:[0-9]{2})', r'\n;\1;', table_str_delim)
		table_str_final = re.sub(r'([0-9]{2} [A-Z][a-z]{2} [0-9]{4})', r'\n\1', table_str_final)
		
		# add delim before result
		table_str_final = re.sub(r'([0-9]:[0-9];)', r';\1', table_str_final)
		
		# remove last delim per line
		table_str_final = table_str_final.replace(";6;\n", ";6\n")
		table_str_final = table_str_final.replace(" 1 X 2 B's;\n", ";;;;;;;\n")
	
		browser.close()
		
		# append data
		data = data + table_str_final


df_l3 = pd.DataFrame([x.split(';') for x in data.split('\n')])




##########  write out   #######################################################

df_l1.to_csv(z_bets_output_src + 'oddsportal_l1.csv', sep=';', encoding='UTF-8', index=False)
df_l2.to_csv(z_bets_output_src + 'oddsportal_l2.csv', sep=';', encoding='UTF-8', index=False)
df_l3.to_csv(z_bets_output_src + 'oddsportal_l3.csv', sep=';', encoding='UTF-8', index=False)
# manual corrections of wrong scraping



###############################################################################
#           2) Prepare data
###############################################################################



# prepare l1 ##################################################################
l1 = pd.read_csv(z_bets_input_src + 'oddsportal_l1.csv', sep=';', encoding='UTF-8', 
                 names = ['date', 'time', 'match', 'result', 'odd_win', 'odd_tie', 'odd_loss', 'bookmakers_odds'],
                 usecols=[0,1,2,3,4,5,6,7], 
                 header=1)

# clean date use substr nad format as date
l1['date_substr'] = l1.date.str[:11]
l1.loc[:,'date'] = l1.loc[:,'date_substr'].ffill()
l1.drop(columns='date_substr', inplace=True)
l1['date'] =pd.to_datetime(l1.date, format='%d %b %Y')

# drop missings 
l1.dropna(axis=0, how='all', inplace=True, subset=['time', 'match', 'result'])

# home team column
l1['home_team']  = l1.match.str.split('-').str[0] # extract
l1['home_team'] = l1.home_team.str.strip() # delete leadingn and trailing zeros 
l1.drop(columns='match', inplace =True)



# prepare l2 ##################################################################
l2 = pd.read_csv(z_bets_input_src + 'oddsportal_l2.csv', sep=';', encoding='UTF-8', 
                 names = ['date', 'time', 'match', 'result', 'odd_win', 'odd_tie', 'odd_loss', 'bookmakers_odds'],
                 usecols=[0,1,2,3,4,5,6,7], 
                 header=1)

# clean date use substr nad format as date
l2['date_substr'] = l2.date.str[:11]
l2.loc[:,'date'] = l2.loc[:,'date_substr'].ffill()
l2.drop(columns='date_substr', inplace=True)
l2['date'] =pd.to_datetime(l2.date, format='%d %b %Y')

# drop missings 
l2.dropna(axis=0, how='all', inplace=True, subset=['time', 'match', 'result'])

# home team column
l2['home_team']  = l2.match.str.split('-').str[0] # extract
l2['home_team'] = l2.home_team.str.strip() # delete leadingn and trailing zeros 
l2.drop(columns='match', inplace =True)


# prepare l3 ##################################################################
l3 = pd.read_csv(z_bets_input_src + 'oddsportal_l3.csv', sep=';', encoding='UTF-8', 
                 names = ['date', 'time', 'match', 'result', 'odd_win', 'odd_tie', 'odd_loss', 'bookmakers_odds'],
                 usecols=[0,1,2,3,4,5,6,7], 
                 header=1)

# clean date use substr nad format as date
l3['date_substr'] = l3.date.str[:11]
l3.loc[:,'date'] = l3.loc[:,'date_substr'].ffill()
l3.drop(columns='date_substr', inplace=True)
l3['date'] =pd.to_datetime(l3.date, format='%d %b %Y')

# drop missings 
l3.dropna(axis=0, how='all', inplace=True, subset=['time', 'match', 'result'])

# home team column
l3['home_team']  = l3.match.str.split('-').str[0] # extract
l3['home_team'] = l3.home_team.str.strip() # delete leadingn and trailing zeros 
l3.drop(columns='match', inplace =True)




# bring dfs together ##########################################################

odds = l1.copy()
odds = odds.append(l2)
odds = odds.append(l3)


#correct data type
odds['odd_loss'] = pd.to_numeric(odds['odd_loss'], errors='coerce')


# make team names homogeneous
odds.home_team = odds.home_team.replace({
    'Alemannia Aachen'       : 'Aachen',
    'Arminia Bielefeld'      : 'Bielefeld',
    'B. Monchengladbach'     : 'Gladbach',
    'Bayer Leverkusen'       : 'Leverkusen',
    'Bayern II'              : 'Bayern München II',
    'Bayern Munich'          : 'Bayern München',
    'Chemnitzer'             : 'Chemnitz',
    'Dusseldorf'             : 'Düsseldorf',
    'Eintracht Frankfurt'    : 'Frankfurt',
    'Energie Cottbus'        : 'Cottbus',
    'FC Koln'                : 'Köln',
    'Fortuna Koln'           : 'Fortuna Köln',
    'Greuther Furth'         : 'Fürth',
    'Grossaspach'            : 'Großaspach',
    'Hallescher'             : 'Halle',
    'Hansa Rostock'          : 'Rostock',
    'Hertha Berlin'          : 'Hertha',
    'Holstein Kiel'          : 'Kiel',
    'Kaiserslautern'         : 'K\'lautern',
    'Karlsruher'             : 'Karlsruhe',
    'Munich 1860'            : '1860 München',
    'Nurnberg'               : 'Nürnberg',
    'Preussen Munster'       : 'Münster',
    'RB Leipzig'             : 'Leipzig',
    'SG Dynamo Dresden'      : 'Dresden',
    'Saarbrucken'            : 'Saarbrücken',
    'Stutt. Kickers'         : 'Stuttgarter Kickers',
    'TuS Koblenz'            : 'Koblenz',
    'Unterhaching'           : 'Haching',
    'VfL Osnabruck'          : 'Osnabrück',
    'Wehen'                  : 'Wehen Wiesbaden',
    'Werder Bremen'          : 'Bremen',
    'Werder Bremen II'       : 'Bremen II'
}) 

    
odds.drop(columns=['time', 'result'], inplace=True)    
odds.sort_values(by='date', inplace=True)


# write-out
odds.to_csv(z_bets_output_final + 'oddsportal_prepared.csv', sep=';', encoding='UTF-8', index=False)









    
    