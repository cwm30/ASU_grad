#Carl Morgenstern
#7/12/2018

#Linear Optimization Script to size a PV and BESS system

#Inputs required:
	#24 hour PV generation profile
	#24 load profile
	#Peak hours based on utility
	#PV cost per kW (plus inverter cost)
	#BESS cost per kWh
	
#Outputs:
	#optimal PV array size
	#optimal BESS size
	
#the goal of this script is to create the cheapest system that will shift all of the load
#outside of the peak hours. It is going to be the first building block of a larger project.


#get peak hours
#get price per kW for PV
#get price per kWh for BESS

#import PV generation
#normalize based on size of PV array
#calculate total normalized generation during peak hours
#plot generation profile

#import load profile
#extract total load (kWh) during peak hours
#plot load profile

#minimize cost of PV array and BESS to fully supply load during peak hours

#plot load profile and generation profile based on optimal size


import numpy as np
from scipy.optimize import minimize
import csv
import sys
import os
import copy
import matplotlib
import matplotlib.pyplot as plt
import pylab
import itertools
import pylab
import datetime
global PVdata
global norm_PVgen_kWh
norm_PVgen_kWh = 0.0
PVdata = []

global loadDays
loadDays = {}

#price per kW
#https://news.energysage.com/how-much-does-the-average-solar-panel-installation-cost-in-the-u-s/
#Including tax credits, it comes out to $2.198/watt
#without tax credits, it is $3.14/watt
PVpp_kw = 2198 #this is after t

#price per kWh for BESS
#IRENA Electriciy storage costs document
#between $200 and $473.
#probably need to get a better estimate on this.

#tesla powerwall 2.
#13.5 kWh capacity
#5900 cost (hardware adds another $700 and installation 800-2000)
#total realistic cost is $7400
#7400/13.5 ~= 550 pp/kWh

BESSpp_kwh = 550

#extract data from PV file and import it into PVdata array
def extract_PVdata(pvFileName):
	
	global PVdata
	pvDict = []
	with open(sys.path[0]+'\\'+pvFileName) as pv:
		list = csv.DictReader(pv)
		for row in list:
			#print (row)
			pvDict.append(row)
		
		timekey = next(itertools.islice(row.keys(), 0, 1))
			
		
		for row in pvDict:
			key =  row.keys()

			temp = {"time": 0.0, "W_norm":""}
			
			#get time into minutes
			temp['time'] = float(row[timekey])*1440
			
			#normalize PV generation
			temp['W_norm'] = float(row['Pac'])/float(row['Size'])
			#print (temp)
			PVdata.append(temp)

#plot the PVdata			
def plot_PVdata():
	
	plt.subplot(2,1,1)
	for i in range(0, len(PVdata)-1):
		row1 = PVdata[i]
		row2 = PVdata[i+1]
		plt.plot([row1["time"],row2['time']],[row1['W_norm'],row2['W_norm']], marker='.', color='green', linestyle='-')
	
	plt.xlabel("Time (minutes)")
	plt.ylabel("normalized PV generation")
	plt.title("PV generation")	
	
		
		
		
def calc_PV_peakhours_gen(peakstart,peakend):
	global norm_PVgen_kWh
	peakstart = 60*peakstart #minutes times start hour
	peakend = 60*peakend #minutes times end hour
	
	peakgen = 0
	totalgen = 0
	
	stopgenflag = False
	
	for row in PVdata:
		
		if row["time"] >= peakstart and row["time"] <= peakend:
			peakgen = peakgen + row["W_norm"]
		totalgen = totalgen + row["W_norm"]

	print ("normalized peak kWh generation:" + str(peakgen/12))
	
	
	#this is the multiplier for the size of the PV system
	#so "norm_PVgen_kWh x Size of PV = kWh generated during peak hours"
	norm_PVgen_kWh = peakgen/12
	return norm_PVgen_kWh
	#print (totalgen)

	
def get_dayType(day,year):
	
	holidays2012 = ["01/02","01/16","02/20","03/30","05/28","07/04","09/03","11/12","11/22","12/25"]
	
	month,date = day.split("/")
	
	if day in holidays2012:
		return "holiday"
	
	elif datetime.date(year,int(month),int(date)).weekday() >= 5:
		return "weekend"
	else:
		return "weekday"
	

def plot_loadDay(loadDay):
	
	
	
	for row in loadDay:
		
		plt.plot(row['time'][:-6],row['kw'], marker='.', color='green')
	

	
	
#data is available of average kW consumption during over 1 hour periods for an entire year
#so extract the data from the CSV
#and separate the days into different lists
#Necessary to keep track of weekday, weekend, holidays.

#for the datasets I have available, I'm going to assume the year is 2012.
def extract_loadData():
	global loadDays
	
	with open(sys.path[0]+'\\PhoenixBASE.csv') as f:	#subject to change but setting it up for this dataset
		list = csv.DictReader(f)
		
		for row in list:
			
			timekey = next(itertools.islice(row.keys(), 0, 1))
			kwKey = next(itertools.islice(row.keys(), 1, 2))

			
			day = row[timekey].split(" ")[1]
			hour = row[timekey].split(" ")[3] 
			
			oneTimeSlot = {'day': day, 'time':hour,'kw':float(row[kwKey]), 'daytype': get_dayType(day,2012)}
			
			try:
				loadDays[day].append(oneTimeSlot)
			except:
				loadDays[day] = []
				loadDays[day].append(oneTimeSlot)
			

def get_peakConsumption(loadDay,peakstart,peakend):
	
	
	peak_kWh = 0
	
	for row in loadDay:
		
		#assuming we only have hourly data
		if int(row['time'][:-6]) > peakstart and int(row['time'][:-6]) <= peakend:
			
			peak_kWh = peak_kWh + row['kw']		#don't need to convert to kWh because its one hour readings
	
	return peak_kWh

def costfunc(params,args):
	load_kWh = args[0]
	PV_peak_kWh_scaler = args[1]
	PVpp_kw = args[2]
	BESSpp_kwh = args[3]
	
	PV_size = params[0]
	#BESS_size = params[1]
	
	#load_kWh = PV_peak_kWh_scaler*PVsize + BESS_size
	#cost = PVpp_kw*PVsize + BESSpp_kWh*BESS_size
	
	#goal is to minimize cost based on variable BESS_size and PVsize
	#constants are PVpp_kw, BESSpp_kwh, load_kWh, and PV_peak_kWh_scaler
	
		
	BESS_size = load_kWh - PV_peak_kWh_scaler*PV_size
	
	cost = PVpp_kw*PV_size + BESSpp_kwh*BESS_size
	print (cost, PV_size, BESS_size)
	return cost
	
	
def BESS_constraint(arg):
	
	print (arg)
	PV_size = arg[0]
	PV_scaler = arg[1]
	load = arg[2]
	BESS_size = arg[3]
	
	return load - (PV_scaler*PV_size + BESS_size)
	
	
if __name__ == "__main__":
	
	pvFileName = sys.argv[1]
	
	extract_PVdata('table.csv')
	plot_PVdata()
	PV_multiplier = calc_PV_peakhours_gen(15,20)

	
	extract_loadData()
	
	
	
	
	plt.subplot(2,1,2)
	#for key in loadDay_keys:
	#	print(key)
	plot_loadDay(loadDays["06/15"])
	
	plt.xlabel("Time (hours)")
	plt.ylabel("KW per Hour Load")
	plt.title("One Year of Load")	
	
	plt.show()
	
	peak_load = get_peakConsumption(loadDays["06/15"],15,20)
	
	#PVpp_kw = BESSpp_kwh*PV_multiplier -1
	
	print (peak_load,PV_multiplier,PVpp_kw,BESSpp_kwh)
	
	constants = [peak_load,PV_multiplier,PVpp_kw,BESSpp_kwh]
	
	PVsize = 3
	BESSsize = peak_load - PV_multiplier
	
	arg = [PVsize,PV_multiplier,peak_load,BESSsize]
	cons = {'type':'eq', 'fun': BESS_constraint(arg)}
	
	results = minimize(costfunc,[PVsize],args=constants, method = 'L-BFGS-B',bounds=((0,peak_load/PV_multiplier),))#,constraints=cons)
	
	print (results)
	if results["success"]:
		print ("success")
		print (list(results['x']))
	
	