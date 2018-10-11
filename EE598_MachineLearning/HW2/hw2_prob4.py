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

def dict_to_array(dict, header):
	
	arr = []
	
	for row in dict:
		arr.append(float(row[header]))
	return arr




if __name__ == "__main__":
	
	BC_data = []
	with open(sys.path[0]+"\\hw2_mpg.csv") as f:
		list = csv.DictReader(f)
		for row in list:
			BC_data.append(row)
	
	
	heads = BC_data[0].keys()
	hd = []
	
	for head in heads:
		hd.append(head)
		# print (hd)
		#print(stat.variance(dict_to_array(BC_data,head)))
	
		# print("Variance "+head+": "+str(stat.variance(dict_to_array(BC_data,head))))
		# print("Mean "+head+": "+str(stat.mean(dict_to_array(BC_data,head))))
	
	
	# problem 3
	mpg = dict_to_array(BC_data, hd[0])
	bin = []
	for i in range(int(min(mpg)),math.ceil(max(mpg))):
		bin.append(i)
	print (bin)
	
	mpg_frq = numpy.zeros((len(bin),), dtype=int)
	for i in range(0,len(bin)):
		for x in mpg:
			if x>=bin[i] and x<bin[i]+1:
				#print(x)
				mpg_frq[i]=1+mpg_frq[i]
				

	plt.bar(bin,mpg_frq,align="edge")
	plt.title("mgps for cars")
	plt.xlabel("frequency")
	plt.ylabel("mpg")
	plt.show()
	
	
	X = numpy.array(mpg)
	X = X.reshape(-1,1)

	
	num_bins = 38
	n, bins, patches = plt.hist(mpg,num_bins,facecolor='blue',alpha=0.2)
	plt.cla()

	plt.bar(bins[:-1],n/sum(n), align="edge")
	#plt.axis([0,50,0,.1])
	gmm = mixture.GaussianMixture(n_components=2, covariance_type='full').fit(X)
	
	weights = gmm.weights_
	means = gmm.means_
	covars = gmm.covariances_
	
	print (means)
	print (covars)
	print (weights)
	x = numpy.linspace(0,50, 1000)

	x = x.reshape(-1,1)
	plt.plot(x,weights[0]*mlab.normpdf(x,means[0],numpy.sqrt(covars[0])), c='red')
	plt.plot(x,weights[1]*mlab.normpdf(x,means[1],numpy.sqrt(covars[1])), c='green')
	plt.plot(x, weights[0]*mlab.normpdf(x,means[0],numpy.sqrt(covars[0])) + weights[1]*mlab.normpdf(x,means[1],numpy.sqrt(covars[1])), c = 'black')
	plt.title("mgps for cars")
	plt.ylabel("% distribution")
	plt.xlabel("mpg")
	
	
	plt.show()
	
	
