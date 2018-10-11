import pandas as pd 
import numpy.linalg as linalg
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sklearn.linear_model as lm
from sklearn.linear_model import Lasso

def text2int(textnum, numwords={}):
	if not numwords:
		units = [
		"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
		"nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
		"sixteen", "seventeen", "eighteen", "nineteen",
		]

		tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

		scales = ["hundred", "thousand", "million", "billion", "trillion"]

		numwords["and"] = (1, 0)
		for idx, word in enumerate(units):    numwords[word] = (1, idx)
		for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
		for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

	current = result = 0
	for word in textnum.split():
		if word not in numwords:
			raise Exception("Illegal word: " + word)

		scale, increment = numwords[word]
		current = current * scale + increment
		if scale > 100:
			result += current
			current = 0

	return result + current




c = pd.read_csv("https://archive.ics.uci.edu/ml/machine-learning-databases/autos/imports-85.data")

#print (c)

  # 1. symboling:                -3, -2, -1, 0, 1, 2, 3.
  # 2. normalized-losses:        continuous from 65 to 256.
  # 3. make:                     alfa-romero, audi, bmw, chevrolet, dodge, honda,
                               # isuzu, jaguar, mazda, mercedes-benz, mercury,
                               # mitsubishi, nissan, peugot, plymouth, porsche,
                               # renault, saab, subaru, toyota, volkswagen, volvo
  # 4. fuel-type:                diesel, gas.
  # 5. aspiration:               std, turbo.
  # 6. num-of-doors:             four, two.
  # 7. body-style:               hardtop, wagon, sedan, hatchback, convertible.
  # 8. drive-wheels:             4wd, fwd, rwd.
  # 9. engine-location:          front, rear.
 # 10. wheel-base:               continuous from 86.6 120.9.
 # 11. length:                   continuous from 141.1 to 208.1.
 # 12. width:                    continuous from 60.3 to 72.3.
 # 13. height:                   continuous from 47.8 to 59.8.
 # 14. curb-weight:              continuous from 1488 to 4066.
 # 15. engine-type:              dohc, dohcv, l, ohc, ohcf, ohcv, rotor.
 # 16. num-of-cylinders:         eight, five, four, six, three, twelve, two.
 # 17. engine-size:              continuous from 61 to 326.
 # 18. fuel-system:              1bbl, 2bbl, 4bbl, idi, mfi, mpfi, spdi, spfi.
 # 19. bore:                     continuous from 2.54 to 3.94.
 # 20. stroke:                   continuous from 2.07 to 4.17.
 # 21. compression-ratio:        continuous from 7 to 23.
 # 22. horsepower:               continuous from 48 to 288.
 # 23. peak-rpm:                 continuous from 4150 to 6600.
 # 24. city-mpg:                 continuous from 13 to 49.
 # 25. highway-mpg:              continuous from 16 to 54.
 # 26. price:                    continuous from 5118 to 45400.


c.columns = ["symboling", "normalized-losses", "make", "fuel-type", "aspiration",
"num-of-doors", "body-style", "drive-wheels", "engine-location","wheel-base", 
"length", "width","height", "curb-weight", "engine-type","num-of-cylinders", "engine-size", "fuel-system","bore", 
"stroke", "compression-ratio", "horsepower", "peak-rpm", "city-mpg", "highway-mpg", "price"]

num_indexes = [0,1,5,9,10,11,12,13,15,16,18,19,20,21,22,23,24,25]

doors = c["num-of-doors"]
cylinder = c["num-of-cylinders"]
for i in range(0,len(doors)):
	if doors[i] != "?":
		doors[i]= text2int(doors[i])
		
	if cylinder[i] != "?":
		cylinder[i] = text2int(cylinder[i])
		

#c["num-of-doors"] = doors
#c["num-of-cylinders"] = cylinder
bins = [-3,-2,-1,0,1,2,3,4]

ax = plt.subplot(6,3,1)
ax.set_title("symboling")
n, bins, patches = plt.hist(c['symboling'], [-3,-2,-1,0,1,2,3],facecolor='blue',alpha=.2,align="left")

c= c.replace('?',np.NaN)

nums_only = pd.DataFrame()
nums_only = nums_only.append(c['symboling'])

for i in range(1,len(num_indexes)):
	ax = plt.subplot(6,3,i+1)
	
	ax.set_title(c.columns[num_indexes[i]])
	
	data = c[c.columns[num_indexes[i]]]
	data = pd.to_numeric(data)
	

	print(c.columns[num_indexes[i]])

	nums_only= nums_only.append(data)
	
	data = data[~np.isnan(data)]
	
	
	
	min = data.min()
	max = data.max()
	
	
	
	n,bin,patch = plt.hist(data,bins="auto",range=(min,max),align="left")
	#print(c.columns[num_indexes[i]],n,min,max)


#plt.bar(bins,n,align="center")

plt.show()


nums_only = nums_only.transpose()
print (nums_only)

nums_only = nums_only.drop("normalized-losses",1)	#remove normalized losses because lots of NaN
nums_only = nums_only.dropna(0,'any')	#remove rows with a NaN

price = nums_only["price"]	#output array
nums_only = nums_only.drop("price",1)	#input array

price_cp = np.array(price)
num_cp = np.array(nums_only)

reg = lm.Ridge(solver="auto",alpha=0.1)	#initialize ridge regression
reg.fit(nums_only, price)	#do the fitting
score = reg.score(nums_only,price)	#extract the scores

print("sum sq error: ",score)
print(reg.coef_)
plt.cla()

for i in range(0,len(nums_only.columns)):
	print(i,nums_only.columns.values[i])

ax = plt.subplot(1,1,1)
ax.set_title("Wieghts of ridge regression. alpha = 0.1")
	
plt.bar(range(0,len(reg.coef_)),reg.coef_)
plt.show()

plt.cla()
###lasso

alp = 100
las = Lasso(alpha=alp)	#initialize lasso regression
las.fit(num_cp, price_cp)	#do the fitting
las_score = las.score(num_cp,price_cp)	#extract the score
print("sum sq error: ",las_score)
print(las.coef_)

ax = plt.subplot(1,1,1)
ax.set_title("Wieghts of Lasso regression. alpha: "+str(alp))
plt.bar(range(0,len(las.coef_)),las.coef_)

plt.show()


alphas = [.0001,.001,.01,.1,1,10,100,100,1000,10000,100000]

for a in alphas:
	las = Lasso(alpha=a)	#initialize lasso regression
	las.fit(num_cp, price_cp)	#do the fitting
	las_score = las.score(num_cp,price_cp)	#extract the score
	
	print("alpha: ",a," sum sq err: ", las_score)
	
	
