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
	

def plot_loadDay(loadDay, col):
	
	

	
	for i in range(0, len(loadDay)-1):
		row1 = loadDay[i]
		row2 = loadDay[i+1]
	
		
		plt.plot([int(row1['time'][:-6]),int(row2['time'][:-6])],[row1['kw'], row2['kw']], marker='.', color=col)
	

	
	
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

	
	
	#considering the constraint that the system MUST be designed to power load during peak hours.
	
	#Money Benefits for PV
	#Energy Bought back: if offpeakgeneration > offpeak load: (OffpeakPVgeneration - Offpeakload) * Buy Back Rate 
	#Offpeak Energy not used: if offpeakload - offpeakgeneration > 0: (offpeakload - offpeakPVgeneration) * offpeakRate
	#Peak energy not used supplied by PV
	
	#Money losses for PV
	#Cost of PV per Day = (Size of PV * Price Per KW) / (Days of LiftimePV)		
		#lifetime of PV might need to be refined.... 
		#can be used on weekends and holidays
		#going to assume 20 years for lifetime
	#Grid Space rental fee = Yearly Fee / 365.25 days
		#.25 accounts for a leap year.
	
	#Money Benefits for BESS
	#Energy Not used during peak hours supplied by Battery
	
	#Money losses for BESS
	#Cost of BESS = Size of Battery * Price per kWh / (LifeTime of BESS)
		#only used during weekdays, so total days used per year to extend the lifetime of the battery.
		#going to assume 10 years for lifetime
	#Charging cost = OffpeakBuyRate*Size of BESS
	
	#Money Benefits Combined
	#Peak Energy Not used: Total Load during peak hours * Peak Rate
	
	
	
	

	
	PVgen_peak_scal = args[0]
	peak_load = args[1]
	PVgen_offpeak_scal = args[2]
	offpeak_load = args[3]
	PVpp_kw = args[4]
	BESSpp_kwh = args[5]
	
	#PV_size <-- size trying to optimize
	PV_size = params[0]
	BESS_size = params[1]
	
	offpeak_gen = PVgen_offpeak_scal * PV_size
	peak_gen = PVgen_peak_scal * PV_size
	
	
	PVlifetime = 20*365.25  #20 years worth of days
	BESSlifetime  = 10*365.25 #10 years worth of days
	peak_buyrate = .24314	#summer months
	offpeak_buyrate = .10873	#summer months
	back_buyrate = .129
	peak_notpaidfor = peak_buyrate * peak_load
	rental_rate_permonth = .93	#per KW 
	grid_rental_perDay = PV_size*rental_rate_permonth * 12 / 365.25
	
	costPV_perDay = (PV_size*PVpp_kw)/PVlifetime + grid_rental_perDay
	
	#Money Benefits for PV
	#Energy Bought back: if offpeakgeneration > offpeak load: (OffpeakPVgeneration - Offpeakload) * Buy Back Rate + Offpeak Load * offpeak buy rate
	#Offpeak Energy not used: if offpeakload - offpeakgeneration > 0: (offpeakload - offpeakPVgeneration) * offpeakRate
		#These are rough total equations. Because the offpeak generation will not match up with the consumption perfectly
		#I should really calculate the difference between the load and generation for each hour and add those up in steps
		#That will need to be a different function though
	
	
	if offpeak_gen > offpeak_load: 
		benefitPV_perDay = (offpeak_gen - offpeak_load) * back_buyrate + offpeak_load * offpeak_buyrate
	else: 
		benefitPV_perDay = (offpeak_load - offpeak_gen) * offpeak_buyrate
	
	benefitPV_perDay = benefitPV_perDay + peak_gen*peak_buyrate
	
	
	costBESS_perDay = ((BESS_size/.8)*BESSpp_kwh)/(BESSlifetime)	#cost of battery per day
	#assuming the battery the smallest battery size necessary and it never degrades
	#this is ok for looking at one day 
	#but will need to be extrapolated to capture the whole picture
	
	#charge to 80%, because after 10 years, the battery will degrade to 80% functionality
	#will also need to be sized to account for that.
	
	costBESS_perDay = costBESS_perDay + (offpeak_buyrate*BESS_size)		#cost to charge battery
	
	benefitBESS_perDay = BESS_size*peak_buyrate		#money saved by not buying power during peak
	
	#peak cost if you have to use energy during peak hours
	if  peak_load > (BESS_size + peak_gen) :  
		peak_cost = (peak_load - (BESS_size + peak_gen))*peak_buyrate
	else: 
		peak_cost = 0
	#minimize total cost, should be negative, or a net gain.
	cost = costPV_perDay + costBESS_perDay + peak_cost - (benefitPV_perDay + benefitBESS_perDay)
	
	#print ("total cost, cost PV, benefit PV, cost BESS, benefit BESS")
	#print (round(cost,3), round(costPV_perDay,3), round(benefitPV_perDay,3), round(costBESS_perDay,3), round(benefitBESS_perDay,3))
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
	#plot_PVdata()
	PV_peak_scal = calc_PV_peakhours_gen(15,20)
	PV_offpeak_scal = calc_PV_peakhours_gen(0,25) - PV_peak_scal
	
	
	extract_loadData()
	
	
	
	
	#plt.subplot(1,2,1)
	#for key in loadDay_keys:
	#	print(key)
	plot_loadDay(loadDays["06/15"],"green")
	
	plt.xlabel("Time (hours)")
	plt.ylabel("KW per Hour Load")
	plt.title("One customer load profile")	
	
	
	
	peak_load = get_peakConsumption(loadDays["06/15"],15,20)
	offpeak_load = get_peakConsumption(loadDays["06/15"],0,25) - peak_load
	
	#PVpp_kw = BESSpp_kwh*PV_multiplier -1
	
	PVpp_kw = 2198
	BESSpp_kwh =550
	
	# for BESSpp_kwh in range(300,910,10):
		# constants = [PV_peak_scal,peak_load,PV_offpeak_scal,offpeak_load,PVpp_kw,BESSpp_kwh]
		# print (constants)
		# print ("Battery pp kwh:",BESSpp_kwh)
		# PVsize = 6
		# BESSsize = 0
		# results = minimize(costfunc,[PVsize,BESSsize],args=constants, method = 'L-BFGS-B',bounds=((0,peak_load/PV_peak_scal),(0,peak_load/.8)))#,constraints=cons)
		# if results["success"]:
		
			# print (list(results['x']))
			# print ("cost:"+ str(round(costfunc(list(results['x']),constants),4)))
			# print ("total peak supplied: ", str(round(list(results['x'])[0]*PV_peak_scal+list(results['x'])[1]*.8,4)))
			# print (" ")
	BESSpp_kwh = 360
	constants = [PV_peak_scal,peak_load,PV_offpeak_scal,offpeak_load,PVpp_kw,BESSpp_kwh]		
	
	plus_bat_load = copy.deepcopy(loadDays["06/15"])
	chrgHrs = 7
	for row in plus_bat_load:
		
		if int(row['time'][:-6]) <= chrgHrs:
			row['kw'] = (peak_load/.9)/(chrgHrs-1)+row['kw']
		elif int(row['time'][:-6]) > 14 and int(row['time'][:-6]) < 20:
			row['kw'] = 0
	#plt.subplot(1,2,2)
	
	
	plot_loadDay(plus_bat_load,"red")
	
	#plt.axis([0,24,0,4.5])
	
	with open("loadBatteryEx.csv","w") as wr:
		for row in loadDays["06/15"]:
			wr.write(str(row['kw']))
			wr.write(",")
		wr.write("\n")
		for row in plus_bat_load:
			wr.write(str(row['kw']))
			wr.write(",")
		wr.write("\n")
		
	
	plt.show()
	
	#arg = [PVsize,PV_multiplier,peak_load,BESSsize]
	#cons = {'type':'eq', 'fun': BESS_constraint(arg)}
	
	# results = minimize(costfunc,[PVsize],args=constants, method = 'L-BFGS-B',bounds=((0,peak_load/PV_peak_scal),))#,constraints=cons)
	
	# print (results)
	# if results["success"]:
		# print ("success")
		# print (list(results['x']))
	
	