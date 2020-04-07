#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 7 2020

@author: marcfabel



Descritpion:
     - read in the data topic-wise, generate panels(AGS,year) -> topic df
         topic df are merged into final df
     
     - be aware: this is just a short version of the normal 
         prepare_regional_database program



Inputs: [source]
     neighbor_regions_prepared.csv                         [intermed_maps]   comes as output from QGIS, which AGS contain a stadium - the neighbors of these regions

	124_current_pop_XXXX.csv                               [source]
	

Outputs:
     regional_data_neighbor_regions_prepared.csv           [final]


"""

# packages
import pandas as pd
import time
start_time = time.time()



# work directories (LOCAL)
#z_regional_source =           'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/source/regional_database/'
#z_regional_output_final =     'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/final/'
#z_maps_input_intermediate =   'C:/Users/fabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'
#z_prefix =                    'soc_ext_'


# HOME directories
z_regional_source =           '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/source/regional_database/'
z_regional_output_final =     '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/final/'
z_maps_input_intermediate =   '/Users/marcfabel/Dropbox/soc_ext_Dx/analysis/data/intermediate/maps/'

z_prefix =                    'soc_ext_'



# magic numbers
z_first_year_wave = 2011
z_last_year_wave = 2015




###############################################################################
#           1) Paths
###############################################################################

z_population =      '12_population/'





###############################################################################
#           DEFINE ACTIVE REGIONS
###############################################################################
# select only active neighbor regions: 
neighbor_regions = pd.read_csv(z_maps_input_intermediate + 'neighbor_regions_prepared.csv', sep=';')
active_neighbor_regions = neighbor_regions['AGS'].drop_duplicates().to_frame()
active_neighbor_regions.sort_values('AGS', inplace=True)
active_neighbor_regions.reset_index(inplace=True, drop=True)
active_neighbor_regions['active'] = 1




###############################################################################
#           12_POPULATION
###############################################################################



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
	pop[year] = pop[year].merge(active_neighbor_regions, on='AGS', how='inner')
	pop[year].drop(['active'], inplace=True, axis=1)
	pop[year]['year'] = year

# make large df from the cross-sections
current_pop = pop[z_first_year_wave].copy()
for year in range(z_first_year_wave+1,z_last_year_wave+1):
    current_pop = current_pop.append(pop[year])


#keep only relevant ones:
current_pop = current_pop[['AGS', 'AGS_Name', 'pop_t', 'pop_f', 'pop_m', 'year']]


# current_pop columns as integeres
current_pop[['pop_t', 'pop_f', 'pop_m']] = current_pop[['pop_t', 'pop_f', 'pop_m']].apply(pd.to_numeric)





########## COMBINE EVERYTHING IN POPULATION DF ##########
population = current_pop.copy()
regional_data = population.copy()





###############################################################################
#           READ OUT
###############################################################################

# reorder columns
z_cols_to_order = ['year', 'AGS', 'AGS_Name', 'pop_t']
z_new_columns = z_cols_to_order + (regional_data.columns.drop(z_cols_to_order).tolist())
regional_data = regional_data[z_new_columns]






# read out
regional_data.to_csv(z_regional_output_final + 
                     'regional_data_neighbor_regions_prepared.csv', 
                     sep=';', encoding='UTF-8', index=False)








###############################################################################
#           END OF FILE
###############################################################################
