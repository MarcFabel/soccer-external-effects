# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 17:38:33 2020

@author: marc fabel


Inputs:
    - 
   
Outputs:
    - 

Updates:
    

"""


# packages
import pandas as pd
import numpy as np
import sklearn



# paths (SERVER)
z_final_data =          'F:/econ/soc_ext/analysis/data/final/'

z_prefix =              'soc_ext_'



# read-in data
dta = pd.read_stata(z_final_data + 'data_prepared.dta')






###############################################################################
#       1) Example with contin forest
###############################################################################
from econml.ortho_forest import ContinuousTreatmentOrthoForest, DiscreteTreatmentOrthoForest
np.random.seed(123)

# simple example
T = np.array([0, 1]*60)
W = np.array([0, 1, 1, 0]*30).reshape(-1, 1)
Y = (.2 * W[:, 0] + 1) * T + .5
est = ContinuousTreatmentOrthoForest(n_trees=1, max_depth=1, subsample_ratio=1,
                                      model_T=sklearn.linear_model.LinearRegression(),
                                      model_Y=sklearn.linear_model.LinearRegression())
est.fit(Y, T, W, W)
print(est.effect(W[:2]))



# advanced example with many confounders
from econml.sklearn_extensions.linear_model import WeightedLasso
import matplotlib.pyplot as plt

X = np.random.uniform(-1, 1, size=(4000, 1))
W = np.random.normal(size=(4000, 50))
support = np.random.choice(50, 4, replace=False)
T = np.dot(W[:, support], np.random.normal(size=4)) + np.random.normal(size=4000)
Y = np.exp(2*X[:, 0]) * T + np.dot(W[:, support], np.random.normal(size=4)) + .5
est = ContinuousTreatmentOrthoForest(n_trees=100,
                                    max_depth=5,
                                    model_Y=WeightedLasso(alpha=0.01),
                                    model_T=WeightedLasso(alpha=0.01))
est.fit(Y, T, X, W)

X_test = np.linspace(-1, 1, 30).reshape(-1, 1)
treatment_effects = est.effect(X_test)
plt.plot(X_test[:, 0], treatment_effects, label='ORF estimate')
plt.plot(X_test[:, 0], np.exp(2*X_test[:, 0]), 'b--', label='True effect')
plt.legend()
plt.show(block=False)



########## get my data in the framework #######################################


# generate controls/confounders  ## W ##
region_fe  = pd.get_dummies(dta['ags'])
time_fe = pd.get_dummies(data=dta[['dow_num', 'month', 'year']],
                         columns=['dow_num', 'month', 'year'])
weather = dta[['tmk', 'txk', 'tnk', 'tgk', 'vpm', 'nm', 'pm', 'upm', 'rs',
              'sdk', 'sh', 'fm']]
holiday = dta[['sch_hday', 'pub_hday', 'special_day']]

temp = dta[['ags', 'dow_num', 'month', 'year']].astype(str)
temp['agsxdow'] = temp['ags'] + temp['dow_num']
temp['agsxmonth'] = temp['ags'] + temp['month']
temp['agsxyear'] = temp['ags'] + temp['year']
temp.drop(['ags', 'dow_num', 'month', 'year'], inplace=True, axis=1)
interaction = pd.get_dummies(temp)

# first try w/o interaction
W = pd.concat([region_fe, time_fe, weather, holiday], axis=1).to_numpy() # , interaction
Y = dta['assrate'].to_numpy()
T = dta['d_gameday'].to_numpy()
X = dta['pop_density'].to_numpy().reshape(-1,1)

est = DiscreteTreatmentOrthoForest(n_trees=100,
                                    max_depth=10,
                                    model_Y=WeightedLasso(alpha=0.01),
                                    propensity_model=sklearn.linear_model.LogisticRegression(max_iter=1000,
                                                                                             solver='lbfgs'))
est.fit(Y, T, X, W)

X_test = np.linspace(0, 5000, 30).reshape(-1, 1)
treatment_effects = est.effect(X_test)
plt.plot(X_test[:, 0], treatment_effects, label='ORF estimate')
plt.legend()
plt.show(block=False)



# XXX: do I have to normalize the variables?
