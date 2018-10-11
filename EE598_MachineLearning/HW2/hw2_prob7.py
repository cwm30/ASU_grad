import sys
import csv
import numpy
import matplotlib.pyplot as plt
import scipy.stats as stats
import copy
import math
import matplotlib.mlab as mlab
from mpl_toolkits.mplot3d import Axes3D
from sklearn import mixture
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import SelectPercentile
import pandas

#load data

with open(sys.path[0]+"\\combined_EV_HH.csv") as f:
	df = pandas.read_csv(f)
	df['Time'] = pandas.to_datetime(df['Time'])
	
	df['Time'] = [d.hour*60 + d.minute for d in df['Time']]

	arr = df.values
	print (arr)
	#arr = numpy.around(arr,3)
	data = arr[:,[0,3]]
	EVcharge = arr[:,1]


	

# feature extraction
test = SelectKBest(score_func=chi2, k='all',)
fit = test.fit(data,EVcharge)

#pandas.set_option('display.float_format', lambda x: '%.3f' % x)
# summarize scores
numpy.set_printoptions(precision=3, suppress=True)
print(fit.scores_)

features = fit.transform(data)