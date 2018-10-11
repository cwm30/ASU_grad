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
import pandas

#load data

with open(sys.path[0]+"\\spam_data.csv") as f:
	df = pandas.read_csv(f)

	arr = df.values
	#arr = numpy.around(arr,3)
	spam_data = arr[:,0:57]
	spam_out = arr[:,57]

	
	

# feature extraction
test = SelectKBest(score_func=chi2, k=10,)
fit = test.fit(spam_data,spam_out)

#pandas.set_option('display.float_format', lambda x: '%.3f' % x)
# summarize scores
numpy.set_printoptions(precision=3, suppress=True)
print(fit.scores_)

ind = fit.get_support(True)
print(ind)
features = fit.transform(spam_data)







