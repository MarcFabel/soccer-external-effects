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
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
#import matplotlib.style as style
import time
start_time = time.time()



# WORK directories
z_regional_source = 'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/source/regional_database/'


# HOME directories
#z_regional_source =                  '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/regional_database/'


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
z_buildings =       '31_buildings/'
z_manufacturing =   '42_manufactoring/'
z_tourism =         '45_tourism/'
z_transport =       '46_transport/'
z_public_budgets =  '71_public_budgets/'







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
elec_ger13 = pd.read_csv(z_regional_source + z_elections + '141_German_2013.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)
elec_ger13.columns = ['date', 'AGS', 'AGS_Name', 'elec_13g_nr_eligibles', 'elec_13g_turnout', 'elec_13g_valid_votes',
                    'cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']
elec_ger13['AGS'] = elec_ger13['AGS'].str.ljust(8, fillchar='0')
elec_ger13['elec_13g_turnout'] = elec_ger13['elec_13g_turnout'].str.replace(',','.')
elec_ger13['AGS'] = elec_ger13['AGS'].astype(int)
elec_ger13 = elec_ger13.merge(active_regions, on='AGS')
elec_ger13 = elec_ger13.apply(pd.to_numeric, errors='coerce')
# have vote shares per party
for party in ['cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']:
	elec_ger13['elec_13g_' + party] = (elec_ger13[party] / elec_ger13['elec_13g_valid_votes']) * 100
	elec_ger13.drop(party, inplace=True, axis=1)
elec_ger13.drop(['date', 'AGS_Name', 'active', 'elec_13g_nr_eligibles', 'elec_13g_valid_votes'], inplace=True, axis=1)

elec_ger17 = pd.read_csv(z_regional_source + z_elections + '141_German_2017.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)
elec_ger17.columns = ['date', 'AGS', 'AGS_Name', 'elec_17g_nr_eligibles', 'elec_17g_turnout', 'elec_17g_valid_votes',
                    'cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']
elec_ger17['AGS'] = elec_ger17['AGS'].str.ljust(8, fillchar='0')
elec_ger17['elec_17g_turnout'] = elec_ger17['elec_17g_turnout'].str.replace(',','.')
elec_ger17['AGS'] = elec_ger17['AGS'].astype(int)
elec_ger17 = elec_ger17.merge(active_regions, on='AGS')
elec_ger17 = elec_ger17.apply(pd.to_numeric, errors='coerce')
# have vote shares per party
for party in ['cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']:
	elec_ger17['elec_17g_' + party] = (elec_ger17[party] / elec_ger17['elec_17g_valid_votes']) * 100
	elec_ger17.drop(party, inplace=True, axis=1)
elec_ger17.drop(['date', 'AGS_Name', 'active', 'elec_17g_nr_eligibles', 'elec_17g_valid_votes'], inplace=True, axis=1)



########## 142_EUROPEAN ##########
elec_eur = pd.read_csv(z_regional_source + z_elections + '142_European_2014.csv',
                     sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)
elec_eur.columns = ['date', 'AGS', 'AGS_Name', 'elec_14e_nr_eligibles', 'elec_14e_turnout', 'elec_14e_valid_votes',
                    'cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']
elec_eur['AGS'] = elec_eur['AGS'].str.ljust(8, fillchar='0')
elec_eur['elec_14e_turnout'] = elec_eur['elec_14e_turnout'].str.replace(',','.')

elec_eur['AGS'] = elec_eur['AGS'].astype(int)
elec_eur = elec_eur.merge(active_regions, on='AGS')
elec_eur = elec_eur.apply(pd.to_numeric, errors='coerce')

# have vote shares per party
for party in ['cdu_csu', 'spd', 'greens', 'fdp', 'linke', 'afd', 'others']:
	elec_eur['elec_14e_' + party] = (elec_eur[party] / elec_eur['elec_14e_valid_votes']) * 100
	elec_eur.drop(party, inplace=True, axis=1)

elec_eur.drop(['date', 'AGS_Name', 'active', 'elec_14e_nr_eligibles', 'elec_14e_valid_votes'], inplace=True, axis=1)




########## COMBINE ELECTION DATA ##########
elections = elec_ger13.copy()
elections = elections.merge(elec_ger17, on='AGS')
elections = elections.merge(elec_eur, on='AGS')





###############################################################################
#           31  BUILDINGS
###############################################################################

########## 311_BUILDINGS_PERMITS ##########
perm= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	perm[year] = pd.read_csv(z_regional_source + z_buildings + '311_permits_' + str(year) + '.csv',
		sep=';', encoding='ISO-8859-1', skiprows=12, skipfooter=4, dtype=str)

	# keep only few columns
	perm[year].columns = list(range(perm[year].shape[1]))
	perm[year] = perm[year][[0, 2, 6, 10]]
	perm[year].rename(columns={0:'AGS', 2:'build_prmts_resid_builds', 6:'build_prmts_flats', 10:'build_prmts_dwelling_area'}, inplace=True)

	# have AGS in the right format (fill up with trailing zeros, str8)
	perm[year]['AGS'] = perm[year]['AGS'].str.ljust(8, fillchar='0')
	perm[year]['AGS'] = perm[year]['AGS'].astype(int)

	perm[year]['build_prmts_dwelling_area'] = perm[year]['build_prmts_dwelling_area'].str.replace(',','.')

	# select only active regions
	perm[year] = perm[year].merge(active_regions, on='AGS', how='inner')
	perm[year].drop(['active'], inplace=True, axis=1)
	perm[year]['year'] = year

# make large df from the cross-sections
buildings_permits = perm[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	buildings_permits = buildings_permits.append(perm[year])

# fill NaNs with zeros
for var in ['build_prmts_resid_builds', 'build_prmts_flats']:
    buildings_permits[var] = buildings_permits[var].str.replace('-', '0')

# buildings_permits columns as integeres
buildings_permits = buildings_permits.apply(pd.to_numeric, errors='coerce')



########## 311_BUILDINGS_COMPLETED ##########
cmpltd= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	cmpltd[year] = pd.read_csv(z_regional_source + z_buildings + '311_construction_completed_' + str(year) + '.csv',
		sep=';', encoding='ISO-8859-1', skiprows=12, skipfooter=4, dtype=str)

	# keep only few columns
	cmpltd[year].columns = list(range(cmpltd[year].shape[1]))
	cmpltd[year] = cmpltd[year][[0, 2, 6, 10]]
	cmpltd[year].rename(columns={0:'AGS', 2:'build_cmpltd_resid_builds', 6:'build_cmpltd_flats', 10:'build_cmpltd_dwelling_area'}, inplace=True)

	# have AGS in the right format (fill up with trailing zeros, str8)
	cmpltd[year]['AGS'] = cmpltd[year]['AGS'].str.ljust(8, fillchar='0')
	cmpltd[year]['AGS'] = cmpltd[year]['AGS'].astype(int)

	cmpltd[year]['build_cmpltd_dwelling_area'] = cmpltd[year]['build_cmpltd_dwelling_area'].str.replace(',','.')

	# select only active regions
	cmpltd[year] = cmpltd[year].merge(active_regions, on='AGS', how='inner')
	cmpltd[year].drop(['active'], inplace=True, axis=1)
	cmpltd[year]['year'] = year

# make large df from the cross-sections
buildings_completed = cmpltd[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	buildings_completed = buildings_completed.append(cmpltd[year])

# fill NaNs with zeros
for var in ['build_cmpltd_resid_builds', 'build_cmpltd_flats']:
    buildings_completed[var] = buildings_completed[var].str.replace('-', '0')

# buildings_completed columns as integeres
buildings_completed = buildings_completed.apply(pd.to_numeric, errors='coerce')



########## 312_STOCK_OF_BUILDINGS_&_DWELLINGS ##########
buildings_stock = pd.read_csv(z_regional_source + z_buildings + '312_stock_buildings.csv',
	sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)

# keep only few columns
buildings_stock.columns = list(range(buildings_stock.shape[1]))
buildings_stock = buildings_stock[[0, 1, 3, 8, 9]]
buildings_stock.rename(columns={0:'date', 1:'AGS', 3:'build_stock_resid_builds', 9:'build_stock_flats', 8:'build_stock_dwelling_area'}, inplace=True)

# drop irrelevent rows
z_delete_rows = buildings_stock[buildings_stock['AGS'] == 'DG'].index
buildings_stock.drop(z_delete_rows, inplace=True)
buildings_stock['year'] = pd.to_numeric(buildings_stock.date.str.slice(-4,))
z_delete_rows = buildings_stock[ (buildings_stock['year'] < z_first_year_wave) | (buildings_stock['year'] > z_last_year_wave)].index
buildings_stock.drop(z_delete_rows, inplace=True)

# correct formats
buildings_stock['AGS'] = buildings_stock['AGS'].str.ljust(8, fillchar='0')
buildings_stock['AGS'] = buildings_stock['AGS'].astype(int)
buildings_stock['build_stock_dwelling_area'] = buildings_stock['build_stock_dwelling_area'].str.replace(',','.')

# select only active regions
buildings_stock = buildings_stock.merge(active_regions, on='AGS', how='inner')
buildings_stock.drop(['active', 'date'], inplace=True, axis=1)

# buildings_stock columns as integeres
buildings_stock = buildings_stock.apply(pd.to_numeric)



########## COMBINE BUILDINGS VARIABLES ##########
buildings = buildings_permits.copy()
buildings = buildings.merge(buildings_completed, on=['AGS', 'year'])
buildings = buildings.merge(buildings_stock, on=['AGS', 'year'])





###############################################################################
#           4 ECONOMIC SECTORS
###############################################################################


########## 421_MANUFACTURING_REPORT ##########
manufacturing = pd.read_csv(z_regional_source + z_manufacturing + '421_manufacturing_report.csv',
	sep=';', encoding='ISO-8859-1', skiprows=7, skipfooter=4, dtype=str)
manufacturing.columns = ['date', 'AGS', 'AGS_Name', 'manuf_firms', 'manuf_employees', 'manuf_gross_pay_thsnd']
# drop irrelevent rows
z_delete_rows = manufacturing[manufacturing['AGS'] == 'DG'].index
manufacturing.drop(z_delete_rows, inplace=True)
manufacturing['year'] = pd.to_numeric(manufacturing.date.str.slice(-4,))
z_delete_rows = manufacturing[ (manufacturing['year'] < z_first_year_wave) | (manufacturing['year'] > z_last_year_wave)].index
manufacturing.drop(z_delete_rows, inplace=True)
# have AGS in the right format (fill up with trailing zeros, str8)
manufacturing['AGS'] = manufacturing['AGS'].str.ljust(8, fillchar='0')
manufacturing['AGS'] = manufacturing['AGS'].astype(int)
# select only active regions
manufacturing = manufacturing.merge(active_regions, on='AGS', how='inner')
manufacturing.drop(['active', 'date', 'AGS_Name'], inplace=True, axis=1)

# manufacturing information is missing for 2 regions (3103000 & 9184148) partly
# ->  mark missings as NaNs |  forward fill per group | still missing replace with mean
manufacturing = manufacturing.replace('.', np.nan)
manufacturing.sort_values(['AGS', 'year'], inplace=True)
for var in ['manuf_employees', 'manuf_gross_pay_thsnd']:
     manufacturing[var] = manufacturing.groupby('AGS')[var].ffill()
manufacturing = manufacturing.apply(pd.to_numeric, errors='coerce')
manufacturing['manuf_gross_pay_thsnd'].fillna(manufacturing['manuf_gross_pay_thsnd'].mean(),
             inplace =True) # affects Braunschweig (3103000)
manufacturing['manuf_gross_pay_thsnd'] = manufacturing['manuf_gross_pay_thsnd'].astype(int)



########## 454_TOURISM_SURVEY ##########
tour= {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	tour[year] = pd.read_csv(z_regional_source + z_tourism + '454_tourism_survey_' + str(year) + '.csv',
		sep=';', encoding='ISO-8859-1', skiprows=8, skipfooter=4, dtype=str)

	tour[year].columns = ['AGS', 'AGS_Name', 'trsm_accomodations', 'trsm_beds', 'trsm_guest_nights', 'trsm_guests']

	# have AGS in the right format (fill up with trailing zeros, str8)
	tour[year]['AGS'] = tour[year]['AGS'].str.ljust(8, fillchar='0')
	tour[year]['AGS'] = tour[year]['AGS'].astype(int)
	# select only active regions
	tour[year] = tour[year].merge(active_regions, on='AGS', how='inner')
	tour[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	tour[year]['year'] = year

# make large df from the cross-sections
tourism = tour[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	tourism = tourism.append(tour[year])

# missing values, first fill forward, set the remaining NaNs as zero, only small areas ( 8119087 Aspach, 8226076 Sandhausen )
tourism.sort_values(['AGS', 'year'], inplace=True)
tourism = tourism.replace('-', '0') # 10043117 Spiesen-Elversberg there are no accomodations
tourism = tourism.replace('.', np.nan)
for var in ['trsm_accomodations', 'trsm_beds', 'trsm_guest_nights', 'trsm_guests']:
     tourism[var] = tourism.groupby('AGS')[var].ffill()     #forward-fill
     tourism[var].fillna('0', inplace=True)                 #remaining nans: set to zero

tourism = tourism.apply(pd.to_numeric)



########## 462_ROAD_TRAFFIC_ACCIDENTS ##########
trans = {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	trans[year] = pd.read_csv(z_regional_source + z_transport + '462_road_traffic_accidents_' + str(year) + '.csv',
		sep=';', encoding='ISO-8859-1', skiprows=8, skipfooter=4, dtype=str)

	trans[year].columns = ['AGS', 'AGS_Name', 'acc_total', 'acc_with_injuries', 'acc_heavy_damage', 'acc_alc_drugs', 'acc_nr_deaths', 'acc_nr_injured']


	# have AGS in the right format (fill up with trailing zeros, str8)
	trans[year]['AGS'] = trans[year]['AGS'].str.ljust(8, fillchar='0')
	trans[year]['AGS'] = trans[year]['AGS'].astype(int)
	# select only active regions
	trans[year] = trans[year].merge(active_regions, on='AGS', how='inner')
	trans[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	trans[year]['year'] = year

# make large df from the cross-sections
transport = trans[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	transport = transport.append(trans[year])

# encode variables as integers
transport.sort_values(['AGS', 'year'], inplace=True)
transport.reset_index(inplace=True, drop=True)
transport = transport.replace('-', '0')
transport = transport.replace('.', np.nan)
for var in ['acc_nr_deaths']: # affects only Jena 2015
     transport[var] = transport.groupby('AGS')[var].ffill()
transport = transport.apply(pd.to_numeric)



########## COMBINE ECONOMIC SECTORS VARIABLES ##########
economic_sectors = manufacturing.copy()
economic_sectors = economic_sectors.merge(tourism, on=['AGS', 'year'])
economic_sectors = economic_sectors.merge(transport, on=['AGS', 'year'])




###############################################################################
#           71 PUBLIC BUDGETS
###############################################################################

########## 712_TAX_BUDGET ##########
tax = {}
for year in range(z_first_year_wave, z_last_year_wave+1):
	tax[year] = pd.read_csv(z_regional_source + z_public_budgets + '712_tax_budget_' + str(year) + '.csv',
		sep=';', encoding='ISO-8859-1', skiprows=10, skipfooter=4, dtype=str)

	tax[year].columns = ['AGS', 'AGS_Name', 'tax_prop_A_revenue_thsnd', 'tax_prop_B_revenue_thsnd', 'tax_trade_revenue_thsnd',
						'tax_prop_A_base_rate_thsnd', 'tax_prop_B_base_rate_thsnd', 'tax_trade_base_rate_thsnd',
						'tax_prop_A_mult_pct', 'tax_prop_B_mult_pct', 'tax_trade_mult_pct',
						'tax_income_share_municip_thsnd', 'tax_sales_share_municip_thsnd', 'tax_trade_levy_thsnd', 'tax_trade_net_thsnd']

	# have AGS in the right format (fill up with trailing zeros, str8)
	tax[year]['AGS'] = tax[year]['AGS'].str.ljust(8, fillchar='0')
	tax[year]['AGS'] = tax[year]['AGS'].astype(int)
	# select only active regions
	tax[year] = tax[year].merge(active_regions, on='AGS', how='inner')
	tax[year].drop(['active', 'AGS_Name'], inplace=True, axis=1)
	tax[year]['year'] = year

# make large df from the cross-sections
tax_budget = tax[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
	tax_budget = tax_budget.append(tax[year])
# encode to numeric and rescale variables in percent
tax_budget = tax_budget.apply(pd.to_numeric)
for var in ['tax_prop_A_mult_pct', 'tax_prop_B_mult_pct', 'tax_trade_mult_pct']:
     tax_budget[var] = tax_budget[var] /10



# XXX einzelne df durchgehen ob die varnames meaningful sind

###############################################################################
#           COMBINE THE DATA
###############################################################################

regional_data = territory.copy()
regional_data = regional_data.merge(population, on=['year', 'AGS'])
regional_data = regional_data.merge(labor_market, on=['year', 'AGS'])
regional_data = regional_data.merge(elections, on='AGS')
regional_data = regional_data.merge(buildings, on=['year', 'AGS'])
regional_data = regional_data.merge(economic_sectors, on=['year', 'AGS'])
regional_data = regional_data.merge(tax_budget, on=['year', 'AGS'])


# reorder columns
z_cols_to_order = ['year', 'AGS', 'AGS_Name', 'area', 'pop_t', 'c11_share_foreigners_t',
                   'births_t', 'deaths_t', 'mig_in_t', 'mig_out_t',
                   'employees_t', 'ue', 'elec_13g_turnout', 'elec_17g_turnout', 'elec_14e_turnout',
                   'build_cmpltd_resid_builds', 'build_stock_flats',
                   'manuf_firms', 'trsm_accomodations', 'acc_total',
                   'tax_trade_revenue_thsnd']
z_new_columns = z_cols_to_order + (regional_data.columns.drop(z_cols_to_order).tolist())
regional_data = regional_data[z_new_columns]



# check whether there are some missing data
print('There are {} variables with missing values'.format(regional_data.isna().sum().sum()))
print("--- %s seconds ---" % (time.time() - start_time))



# XXX ideas of constructing variables
# population density
# D_negative_netto_migration
# D_more_deaths_than_births
# number of births per women aged 15_40, was soll das genau sagen
# (un-)employment rate
# number of dwellings per person, indicates wohnungsnot
# manuf_firms/person
# trsm_accomodations / person
# acc_total / person

###############################################################################
#           END OF FILE
###############################################################################



# XXX to do:
#   - Anere Datenquellen:
#       - 1) Bundesagentur für Arbeit die noch interessant sein könnten? zb Sozialleistungen
#       - 2) Regionalatlas
#   - DESTATIS fragen was mit den fehlenden Jahren in den Tabellen 731_wage_income_statistics und 715_cash_results ist