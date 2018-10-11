import sys
import csv
import numpy
import matplotlib.pyplot as plt
import statistics as stat
import copy
import math
import matplotlib.mlab as mlab
from mpl_toolkits.mplot3d import Axes3D


def dict_to_array(dict, header):
	
	arr = []
	
	for row in dict:
		arr.append(int(row[header]))
	return arr




if __name__ == "__main__":
	
	BC_data = []
	with open(sys.path[0]+"\\hw2_breastcancerdata.csv") as f:
		list = csv.DictReader(f)
		for row in list:
			BC_data.append(row)
	
	
	heads = BC_data[0].keys()
	hd = []
	
	for head in heads:
		hd.append(head)
		print (hd)
		#print(stat.variance(dict_to_array(BC_data,head)))
	
		print("Variance "+head+": "+str(stat.variance(dict_to_array(BC_data,head))))
		print("Mean "+head+": "+str(stat.mean(dict_to_array(BC_data,head))))
	
	
	#problem 6
	
	list1 = dict_to_array(BC_data,hd[0])
	o1 = stat.variance(list1)
	u1 = stat.mean(list1)
	
	list2 = dict_to_array(BC_data,hd[1])
	o2 = stat.variance(list2)
	u2 = stat.mean(list2)
	
	p = numpy.corrcoef(list1,list2)[1,0]
	print("correlation coefficient:" +str(p))
	
	

	#problem 7
	
	#fill bin1 sequence
	bin1 = []
	for b in list1:
		if b not in bin1:
			bin1.append(b)
			
	print (bin1)
	
	bin2 = []
	for b in list2:
		if b not in bin2:
			bin2.append(b)
	
	bin1.sort()
	bin2.sort()
	
	print (bin2)
	
	jointProbs, edges = numpy.histogramdd((list1,list2),(bin1,bin2))
	
	jptot = sum(sum(jointProbs))

	list2_mg = [0] * (len(bin2)-1)
	age = []
	for row in jointProbs:
		age.append(sum(row))
		for i in range(0 , len(bin2)-1):
			list2_mg[i] = list2_mg[i]+row[i]
	

	
	
	o2_mg = stat.variance(list2_mg/jptot)
	u2_mg = stat.mean(list2_mg/jptot)
	print("marginalized op year. variance: "+str(o2_mg)+" mean: "+str(u2_mg))
	
	#problem 8
	#age
	
	#fig, ax = plt.subplots(1,2,sharey=True,tight_layout=True)
	
	# ax[0].bar(bin1[:-1],age, align="edge")
	# ax[0].set_title("age of patients")
	# ax[0].set_ylabel("frequency")
	#plt.subplot(1,2,1)
	# ax[1].set_title("age of patient")
	# ax[1].bar(bin2[:-1],list2_mg, align="edge")
	
	#plt.subplot(1,2,2)
	#plt.title("year of experiment")
	
	#
	
	plt.bar(bin1[:-1],age/sum(age), align="edge")
	sig1 = math.sqrt(o1)
	x1 = numpy.linspace(u1 - 3*sig1,u1 +3*sig1,1000)
	plt.plot(x1,mlab.normpdf(x1,u1,sig1))
	plt.title("age of patients")

	plt.show()
	
	plt.bar(bin2[:-1],list2_mg/sum(list2_mg),align="edge")
	sig2 = math.sqrt(o1)
	x2 = numpy.linspace(u2 - 3*sig2,u2 +3*sig2,1000)
	plt.plot(x2,mlab.normpdf(x2,u2,sig2))
	plt.title("year of experiment patients")
	plt.show()
	
	#problem 9
	
	jp_arr = numpy.array(jointProbs)
	
	fig = plt.figure()
	ax = fig.add_subplot(111,projection='3d')
	
	x_data, y_data = numpy.meshgrid(numpy.arange(jp_arr.shape[1]),numpy.arange(jp_arr.shape[0]))
	x_data = x_data.flatten()
	y_data = y_data.flatten()
	z_data = jp_arr.flatten()
	
	ax.bar3d(x_data,y_data,numpy.zeros(len(z_data)),.5,1,z_data)
	
	
	plt.show()
	
