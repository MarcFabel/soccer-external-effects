#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 11:55:41 2019

@author: marcfabel



Steps:

     
     
Inputs:  

         
Updates: 
     
"""

# packages
import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#import matplotlib.style as style



# WORK directories
#z_regional_source = 'F:/econ/soc_ext/analysis/data/source/regional_database/'


# HOME directories
z_regional_source =                  '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/regional_database/'


z_prefix =                          'soc_ext_'

# magic numbers
z_first_year_wave = 2011
z_last_year_wave = 2015




###############################################################################
#           1) Paths 
###############################################################################

z_territory =       '11_territory/'
z_population =      '12_population/'
z_labor_market =    '13_labor_market/'
z_elections =       '14_elections/'
#education =         "05 - Bildung/"
#buildings =         "10 - Gebäude/"
#accidents =         "11 - Verkehr/"
#tourism =           "12 - Tourismus/"
#industry_sector =   "13 - Wirtschaftszweig/nach Wirtschaftszweig/"






# XXX adjust path! comes from z_map_stadiums_AGS; only taken here in a temporary manner
active_regions =pd.read_csv(z_regional_source + 'temp_active_regions.csv', sep=';', encoding='UTF-8')



###############################################################################
#           11_TERRITORY [IN SQUARE KILOMETERS]
###############################################################################

territory = pd.read_csv(z_regional_source + z_territory + 'territorial_area.csv',
                        sep=';', encoding='ISO-8859-1', dtype=str, skiprows=6, skipfooter=4) 
territory.columns=['date', 'AGS', 'AGS_Name', 'area']

# drop irrelevent rows
z_delete_rows = territory[territory['AGS'] == 'DG'].index
territory.drop(z_delete_rows, inplace=True)
territory['year'] = pd.to_numeric(territory.date.str.slice(-4,))
z_delete_rows = territory[ (territory['year'] < z_first_year_wave) | (territory['year'] > z_last_year_wave)].index
territory.drop(z_delete_rows, inplace=True)


# encode the variables
territory['AGS'] = territory['AGS'].str.ljust(8, fillchar='0')
territory['area'] = territory['area'].str.replace(',','.')
territory['AGS'] = territory['AGS'].astype(int)
territory['area'] = pd.to_numeric(territory['area'], errors='coerce')

# keep only relevant regions
territory = territory.merge(active_regions, on='AGS', how='inner')

territory.drop(['date', 'active'], inplace=True, axis=1)
territory = territory[['year', 'AGS', 'AGS_Name', 'area']]
territory.sort_values(['year', 'AGS'], inplace=True)
territory.reset_index(inplace=True, drop=True)





###############################################################################
#           12_POPULATION
###############################################################################
# CONTAINS: 121_CENSUS, 124_CURRENT_POPULATION, 126_BIRTHS, 126_DEATHS, 127_MIGRATION


########## 121_CENSUS ##########
census = pd.read_csv(z_regional_source + z_population + '121_census_2011.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=9, skipfooter=3, dtype=str)
census.columns = ['AGS', 'AGS_Name', 'c11_pop_total', 'c11_pop_male', 'c11_pop_female',
                  'c11_pop_total_ger', 'c11_pop_male_ger', 'c11_pop_female_ger',
                  'c11_pop_total_for', 'c11_pop_male_for', 'c11_pop_female_for']
census.drop(['c11_pop_total_ger', 'c11_pop_male_ger', 'c11_pop_female_ger', 'AGS_Name'], inplace=True, axis=1)
census = census.apply(pd.to_numeric,errors='coerce')

# construct share foreigners
census['c11_share_foreigners_t'] = census['c11_pop_total_for'] / census['c11_pop_total']
census['c11_share_foreigners_m'] = census['c11_pop_male_for'] / census['c11_pop_male']
census['c11_share_foreigners_f'] = census['c11_pop_female_for'] / census['c11_pop_female']

census = census.merge(active_regions, on='AGS')
census = census[['AGS', 'c11_share_foreigners_t','c11_share_foreigners_m','c11_share_foreigners_f']].copy()



########## 124_CURRENT_POPULATION ##########    
# dictionary with all years
pop= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	pop[year] = pd.read_csv(z_regional_source + z_population + '124_current_pop_' + str(year) + '.csv', 
		sep=';', encoding='ISO-8859-1', skiprows=9, skipfooter=4, dtype=str)
 
	pop[year].columns = ['AGS', 'AGS_Name', 'pop_0_2_t', 'pop_3_5_t', 'pop_6_9_t', 'pop_10_14_t', 'pop_15_17_t', 'pop_18_19_t', 'pop_20_24_t', 
		'pop_25_29_t', 'pop_30_34_t', 'pop_35_39_t', 'pop_40_44_t' , 'pop_45_49_t', 'pop_50_54_t', 'pop_55_59_t', 
		'pop_60_64_t', 'pop_65_74_t', 'pop_74+_t', 'pop_t',

		'pop_0_2_m', 'pop_3_5_m', 'pop_6_9_m', 'pop_10_14_m', 'pop_15_17_m', 'pop_18_19_m', 'pop_20_24_m', 
		'pop_25_29_m', 'pop_30_34_m', 'pop_35_39_m', 'pop_40_44_m' , 'pop_45_49_m', 'pop_50_54_m', 'pop_55_59_m', 
		'pop_60_64_m', 'pop_65_74_m', 'pop_74+_m', 'pop_m',		

		'pop_0_2_f', 'pop_3_5_f', 'pop_6_9_f', 'pop_10_14_f', 'pop_15_17_f', 'pop_18_19_f', 'pop_20_24_f', 
		'pop_25_29_f', 'pop_30_34_f', 'pop_35_39_f', 'pop_40_44_f' , 'pop_45_49_f', 'pop_50_54_f', 'pop_55_59_f', 
		'pop_60_64_f', 'pop_65_74_f', 'pop_74+_f', 'pop_f']

	# have AGS in the right format (fill up with trailing zeros, str8)
	pop[year]['AGS'] = pop[year]['AGS'].str.ljust(8, fillchar='0')
	pop[year]['AGS'] = pop[year]['AGS'].astype(int)
		
	# select only active regions
	pop[year] = pop[year].merge(active_regions, on='AGS', how='inner')
	pop[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	pop[year]['year'] = year
    
# make large df from the cross-sections
current_pop = pop[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
    current_pop = current_pop.append(pop[year])

# current_pop columns as integeres
current_pop = current_pop.apply(pd.to_numeric)



########## 126_BIRTHS ##########
births = pd.read_csv(z_regional_source + z_population + '126_births.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=7, skipfooter=4, dtype=str)
births.columns = ['year', 'AGS', 'AGS_Name', 'births_t', 'births_m', 'births_f']
births.drop('AGS_Name', inplace=True, axis=1)

# drop irrelevent rows
z_delete_rows = births[births['AGS'] == 'DG'].index
births.drop(z_delete_rows, inplace=True)
births['AGS'] = births['AGS'].str.ljust(8, fillchar='0')

births['year'] = births['year'].astype(int)
z_delete_rows = births[ (births['year'] < z_first_year_wave) | (births['year'] > z_last_year_wave)].index
births.drop(z_delete_rows, inplace=True)

# drop irrelevent regions
births['AGS'] = births['AGS'].astype(int)
births = births.merge(active_regions, on=['AGS'])
births.drop('active', inplace=True, axis=1)

births = births.apply(pd.to_numeric, errors='coerce')



########## 126_DEATHS ##########
deaths = pd.read_csv(z_regional_source + z_population + '126_deaths.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=8, skipfooter=4, dtype=str)
deaths.columns = ['year', 'AGS', 'AGS_Name', 'deaths_t', 'deaths_m', 'deaths_f']
deaths.drop('AGS_Name', inplace=True, axis=1)

# drop irrelevent rows
z_delete_rows = deaths[deaths['AGS'] == 'DG'].index
deaths.drop(z_delete_rows, inplace=True)
deaths['AGS'] = deaths['AGS'].str.ljust(8, fillchar='0')

deaths['year'] = deaths['year'].astype(int)
z_delete_rows = deaths[ (deaths['year'] < z_first_year_wave) | (deaths['year'] > z_last_year_wave)].index
deaths.drop(z_delete_rows, inplace=True)

# drop irrelevent regions
deaths['AGS'] = deaths['AGS'].astype(int)
deaths = deaths.merge(active_regions, on=['AGS'])
deaths.drop('active', inplace=True, axis=1)

deaths = deaths.apply(pd.to_numeric, errors='coerce')



########## 127_MIGRATION ##########
# dictionary with all years
mig= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	mig[year] = pd.read_csv(z_regional_source + z_population + '127_migration_' + str(year) + '.csv', 
		sep=';', encoding='ISO-8859-1', skiprows=12, skipfooter=7, dtype=str)

	mig[year].columns = ['AGS', 'AGS_Name', 'mig_in_0_17_t', 'mig_in_18_24_t', 'mig_in_25_29_t', 'mig_in_30_49_t', 'mig_in_50_64_t', 'mig_in_65+_t', 'mig_in_t',
					'mig_in_0_17_m', 'mig_in_18_24_m', 'mig_in_25_29_m', 'mig_in_30_49_m', 'mig_in_50_64_m', 'mig_in_65+_m', 'mig_in_m', 
					'mig_in_0_17_f', 'mig_in_18_24_f', 'mig_in_25_29_f', 'mig_in_30_49_f', 'mig_in_50_64_f', 'mig_in_65+_f', 'mig_in_f', 

					'mig_out_0_17_t', 'mig_out_18_24_t', 'mig_out_25_29_t', 'mig_out_30_49_t', 'mig_out_50_64_t', 'mig_out_65+_t', 'mig_out_t',
					'mig_out_0_17_m', 'mig_out_18_24_m', 'mig_out_25_29_m', 'mig_out_30_49_m', 'mig_out_50_64_m', 'mig_out_65+_m', 'mig_out_m', 
					'mig_out_0_17_f', 'mig_out_18_24_f', 'mig_out_25_29_f', 'mig_out_30_49_f', 'mig_out_50_64_f', 'mig_out_65+_f', 'mig_out_f']

	# have AGS in the right format (fill up with trailing zeros, str8)
	mig[year]['AGS'] = mig[year]['AGS'].str.ljust(8, fillchar='0')
	mig[year]['AGS'] = mig[year]['AGS'].astype(int)
		
	# select only active regions
	mig[year] = mig[year].merge(active_regions, on='AGS', how='inner')
	mig[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	mig[year]['year'] = year

# make large df from the cross-sections
migration = mig[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	migration = migration.append(mig[year])

# source data is missing information for 10041100 (Saarbruecken) in 2012, can be calculated via the other regions in the 10041 regionalverband Saarbrücken - just the capital is missing
temp = '10041100	1209	3572	2316	3244	854	377	11572	613	1608	1226	1800	478	166	5891	596	1964	1090	1444	376	211	5681	1190	2205	2196	3614	847	485	10537	615	942	1057	2017	484	189	5304	575	1263	1139	1597	363	296	5233	2012'
# entries are delimited by tab
z_mig = pd.DataFrame([temp.split('\t')])
z_mig.columns = migration.columns
migration.reset_index(inplace=True, drop=True)
migration.drop( migration[ (migration['year'] == 2012) & (migration['AGS'] == 10041100) ].index, inplace=True)
migration = migration.append(z_mig)

# migration columns as integeres
migration = migration.apply(pd.to_numeric, errors='coerce')



########## COMBINE EVERYTHING IN POPULATION DF ##########
population = current_pop.copy()
population = population.merge(census, on='AGS')
population = population.merge(births, on=['year', 'AGS'])
population = population.merge(deaths, on=['year', 'AGS'])
population = population.merge(migration, on=['year', 'AGS'])






###############################################################################
#           13_LABOR_MARKET
###############################################################################
# contains 131_employees and 132_unemployment

########## 131_EMPLOYMENT (at the place of work) ##########
emp= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	emp[year] = pd.read_csv(z_regional_source + z_labor_market + '131_employment_' + str(year) + '.csv', 
		sep=';', encoding='ISO-8859-1', skiprows=11, skipfooter=4, dtype=str)

	emp[year].columns = ['AGS', 'AGS_Name', 'employees_t', 'employees_m', 'employees_f',
						'employees_for_t', 'employees_for_m', 'employees_for_f']

	# have AGS in the right format (fill up with trailing zeros, str8)
	emp[year]['AGS'] = emp[year]['AGS'].str.ljust(8, fillchar='0')
	emp[year]['AGS'] = emp[year]['AGS'].astype(int)
		
	# select only active regions
	emp[year] = emp[year].merge(active_regions, on='AGS', how='inner')
	emp[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	emp[year]['year'] = year

# make large df from the cross-sections
employment = emp[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	employment = employment.append(emp[year])

# employment columns as integeres
employment = employment.apply(pd.to_numeric)




########## 132_UNEMPLOYMENT ##########
uemp= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	uemp[year] = pd.read_csv(z_regional_source + z_labor_market + '132_ue_' + str(year) + '.csv', 
		sep=';', encoding='ISO-8859-1', skiprows=9, skipfooter=4, dtype=str)

	uemp[year].columns = ['AGS', 'AGS_Name', 'ue', 'ue_for', 'ue_disabled', 'ue_15_19', 'ue_15_24', 'ue_55_64', 'ue_longterm']

	# have AGS in the right format (fill up with trailing zeros, str8)
	uemp[year]['AGS'] = uemp[year]['AGS'].str.ljust(8, fillchar='0')
	uemp[year]['AGS'] = uemp[year]['AGS'].astype(int)
		
	# select only active regions
	uemp[year] = uemp[year].merge(active_regions, on='AGS', how='inner')
	uemp[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	uemp[year]['year'] = year

# make large df from the cross-sections
unemployment = uemp[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	unemployment = unemployment.append(uemp[year])

# unemployment columns as integeres
unemployment = unemployment.apply(pd.to_numeric)



########## COMBINE LM DATA ##########
labor_market = employment.copy()
labor_market = labor_market.merge(unemployment, on=['year', 'AGS'])










###############################################################################
#           14 ELECTIONS
###############################################################################



########## 141_GERMAN ##########
elec_ger = pd.read_csv(z_regional_source + z_elections + '141_German_2013.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)
elec_ger.columns = ['date', 'AGS', 'AGS_Name', '13g_nr_eligibles', '13g_turnout', '13g_valid_votes', 
                    'cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']
elec_ger['AGS'] = elec_ger['AGS'].str.ljust(8, fillchar='0')
elec_ger['13g_turnout'] = elec_ger['13g_turnout'].str.replace(',','.')
elec_ger['AGS'] = elec_ger['AGS'].astype(int)
elec_ger = elec_ger.merge(active_regions, on='AGS')
elec_ger = elec_ger.apply(pd.to_numeric, errors='coerce')
# have vote shares per party
for party in ['cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']: 
	elec_ger['13g_' + party] = (elec_ger[party] / elec_ger['13g_valid_votes']) * 100
	elec_ger.drop(party, inplace=True, axis=1)
elec_ger.drop(['date', 'AGS_Name', 'active', '13g_nr_eligibles', '13g_valid_votes'], inplace=True, axis=1)



########## 142_EUROPEAN ##########
elec_eur = pd.read_csv(z_regional_source + z_elections + '142_European_2014.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)
elec_eur.columns = ['date', 'AGS', 'AGS_Name', '14e_nr_eligibles', '14e_turnout', '14e_valid_votes', 
                    'cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']
elec_eur['AGS'] = elec_eur['AGS'].str.ljust(8, fillchar='0')
elec_eur['14e_turnout'] = elec_eur['14e_turnout'].str.replace(',','.')

elec_eur['AGS'] = elec_eur['AGS'].astype(int)
elec_eur = elec_eur.merge(active_regions, on='AGS')
elec_eur = elec_eur.apply(pd.to_numeric, errors='coerce')

# have vote shares per party
for party in ['cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']: 
	elec_eur['14e_' + party] = (elec_eur[party] / elec_eur['14e_valid_votes']) * 100
	elec_eur.drop(party, inplace=True, axis=1)

elec_eur.drop(['date', 'AGS_Name', 'active', '14e_nr_eligibles', '14e_valid_votes'], inplace=True, axis=1)




########## COMBINE ELECTION DATA ##########
elections = elec_ger.copy()
elections = elections.merge(elec_eur, on='AGS')







###############################################################################
#           COMBINE THE DATA
###############################################################################

regional_data = territory.copy()
regional_data = regional_data.merge(population, on=['year', 'AGS'])
regional_data = regional_data.merge(labor_market, on=['year', 'AGS'])
regional_data = regional_data.merge(elections, on='AGS')


# reorder columns
z_cols_to_order = ['year', 'AGS', 'AGS_Name', 'area', 'pop_t', 'c11_share_foreigners_t',
                   'births_t', 'deaths_t', 'mig_in_t', 'mig_out_t',
                   'employees_t', 'ue', '13g_turnout', '14e_turnout']
z_new_columns = z_cols_to_order + (regional_data.columns.drop(z_cols_to_order).tolist())
regional_data = regional_data[z_new_columns]



# check whether there are some missing data
print('There are {} variables with mssing values'.format(regional_data.isna().sum().sum()))



# XXX ideas of constructing variables
# population density
# D_negative_netto_migration
# D_more_deaths_than_births
# number of births per women aged 15_40, was soll das genau sagen
# (un-)employment rate

###############################################################################
#           END OF FILE
###############################################################################



# to do: