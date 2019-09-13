# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:16 2019

This program reads in regions (gemeinden) and compares their availability over
time.

@author: Marc Fabel
"""

# packages
import pandas as pd
import numpy as np

# paths
regions_source = 'F:/econ/soc_ext/analysis/data/BKA/Kataloge-Datenblatt_EDS_Opfer_'
regions_output = 'F:/econ/soc_ext/analysis/output/data/intermediate/'

# home paths irrelevant (data only on server)

###############################################################################
#       1) Read in regions
###############################################################################
# not possible to put in loops as the single years are too different


########## 2011 ##########
df11=pd.read_excel(regions_source + '2011' +'/' + '02_Gemeindekat_12.xls')
col_drop = ['Der Schlüssel ist folgendermassen aufgebaut:', 'Unnamed: 4', 'Unnamed: 6',
       'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9']
df11.drop(col_drop, axis=1, inplace=True)
df11.rename(columns={
        'BKA, KI 12 / INPOL-A-PKS_EDS (ab 01.01.2011)':'satz11',
        'Unnamed: 1' : 'ags',
        'Unnamed: 2' : 'name11',
        'Unnamed: 3' : 'von11'}, inplace=True)

df11 = df11.iloc[11:]
df11[['satz11', 'ags']] = df11[['satz11', 'ags']].astype(int)
df11 = df11[df11['satz11'] == 60]
df11.drop('satz11', axis=1, inplace=True)
df11['y11'] = int(11)


########## 2012 ##########
df12=pd.read_excel(regions_source + '2012' +'/' + '02_Gemeindekat_12.xls')
df12.drop(col_drop, axis=1, inplace=True)
df12.rename(columns={
        'BKA, KI 12 / INPOL-A-PKS_EDS (ab 01.01.2012)':'satz12',
        'Unnamed: 1' : 'ags',
        'Unnamed: 2' : 'name12',
        'Unnamed: 3' : 'von12',
        'Unnamed: 4' : 'bis12'}, inplace=True)
df12 = df12.iloc[11:]
df12[['satz12', 'ags']] = df12[['satz12', 'ags']].astype(int)
df12 = df12[df12['satz12'] == 60]
df12.drop('satz12', axis=1, inplace=True)
df12['y12'] = int(12)

########## 2013 ##########
df13=pd.read_excel(regions_source + '2013' +'/' + '02_Gemeindekat_13.xlsx')
col_drop = ['Der Schlüssel ist folgendermassen aufgebaut:', 'Unnamed: 4', 'Unnamed: 6',
       'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10']
df13.drop(col_drop, axis=1, inplace=True)
df13.rename(columns={
        'BKA, KI 12 / INPOL-A-PKS_EDS (ab 01.01.2013)':'satz13',
        'Unnamed: 1' : 'ags',
        'Unnamed: 2' : 'name13',
        'Unnamed: 3' : 'von13'}, inplace=True)
df13 = df13.iloc[11:]
df13[['satz13', 'ags']] = df13[['satz13', 'ags']].astype(int)
df13 = df13[df13['satz13'] == 60]
df13.drop('satz13', axis=1, inplace=True)
df13['y13'] = int(13)

########## 2014 ##########
df14=pd.read_excel(regions_source + '2014' +'/' + '02_Gemeindekat_14.xlsx')
col_drop = ['Der Schlüssel ist folgendermassen aufgebaut:', 'Unnamed: 5', 'Unnamed: 6',
       'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9']
df14.drop(col_drop, axis=1, inplace=True)
df14.rename(columns={
        'BKA, KI 12 / INPOL-A-PKS_EDS':'satz14',
        'Unnamed: 1' : 'ags',
        'Unnamed: 2' : 'name14',
        'Unnamed: 4' : 'von14'}, inplace=True)
df14 = df14.iloc[11:]
df14[['satz14', 'ags']] = df14[['satz14', 'ags']].astype(int)
df14 = df14[df14['satz14'] == 60]
df14.drop('satz14', axis=1, inplace=True)
df14['y14'] = int(14)


########## 2015 ##########
df15=pd.read_excel(regions_source + '2015' +'/' + '02_Gemeindekat_15.xlsx')
col_drop = ['Der Schlüssel ist folgendermassen aufgebaut:', 'Unnamed: 5', 'Unnamed: 6']
df15.drop(col_drop, axis=1, inplace=True)
df15.rename(columns={
        'BKA, KI 12 / INPOL-A-PKS_EDS':'satz15',
        'Unnamed: 1' : 'ags',
        'Unnamed: 2' : 'name15',
        'Unnamed: 4' : 'von15'}, inplace=True)
df15 = df15.iloc[12:]
df15[['satz15', 'ags']] = df15[['satz15', 'ags']].astype(int)
df15 = df15[df15['satz15'] == 60]
df15.drop('satz15', axis=1, inplace=True)
df15['y15'] = int(15)




###############################################################################
#       2) Put together large Data Frame
###############################################################################
df = df11.merge(df12, on=['ags'], how='outer', indicator=True)
df.rename(columns={'_merge':'_m_11-12'}, inplace=True)
df = df.merge(df13, on=['ags'], how='outer', indicator=True)
df.rename(columns={'_merge':'_m_11-13'}, inplace=True)
df = df.merge(df14, on=['ags'], how='outer', indicator=True)
df.rename(columns={'_merge':'_m_11-14'}, inplace=True)
df = df.merge(df15, on=['ags'], how='outer', indicator=True)
df.rename(columns={'_merge':'_m_11-15'}, inplace=True)
# the most changes happen between 2011 + 2012, between the other years there are less changes



# generate dummy variable when all years are present -> can be inspectedin QGIS
df['D_all_years'] = np.where( (df['y11'].notnull()) & (df['y15'].notnull()), 1, 0)


df = df [['ags', 'name11', 'D_all_years', 'y11', 'y12', 'y13',  'y14', 'y15',
          '_m_11-12', '_m_11-13', '_m_11-14',  '_m_11-15',
        'name12','name13', 'name14', 'name15',
       'von11', 'von12', 'von13', 'von14', 'von15',
       ]]

df = df[['ags', 'name11', 'D_all_years']]

df.drop(df[df['D_all_years'] == 0].index, inplace=True)

# apply format in order to have leading zeros
df['ags']=df['ags'].apply(lambda x: '{0:0>8}'.format(x))

df.rename(columns={'ags':'AGS'}, inplace=True)

df.to_csv(regions_output + 'ags_2011_availabilty_over_years.csv', sep=';')

###############################################################################
#       END OF FILE
###############################################################################


# eher interessant
# 2013 kommentare
# 2014 extra Spalte J/N

