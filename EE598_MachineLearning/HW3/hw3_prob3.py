import numpy.linalg as linalg
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# fig = plt.figure()
# ax = fig.add_subplot(111,projection='3d')


def w_func(x,y,z,a1,a2,a3):
	
	for i in range(0,len(x)):
		w.append([x[i]**2,x[i],1,z[i]])
	
	w= np.asarray(w)
	
	new_points
	
	

data1 = [[2,3,5],[3,4,6],[4,5,7]]
data1 = np.array(data1)
x = data1[:,0]
y = data1[:,1]
z = data1[:,2]


data = [[4,2,1,5],[9,3,1,6],[16,4,1,7]]

p1 = data[0]
p2= data[1]
p3 = data[2]
arr = np.array(data)
ps = arr[:,0:3]
sol = arr[:,3]


 


a,b,c = linalg.lstsq(ps,sol)[0]

print(linalg.lstsq(ps,sol))
print(a,b,c)

x_space = np.linspace(0,5,100)
y_space = np.zeros(100)
#y_space = np.linspace(0,10,100)
z_curve = a*x_space**2 + b*x_space + c

xx, yy = np.meshgrid(range(5),range(0,7))



zz = (-a*xx*xx-b*xx -c)*1./(-1)


for d in data1:
	dline = d[0]

error = 0
for d in y:
	print (d,d**2)
	error = d**2 + error
print (error)

#s = np.sum()

plt3d = plt.figure()
ax = plt3d.gca(projection='3d')

ax.plot_surface(xx,yy,zz,color="lightgrey")

ax.plot(x_space,y_space,z_curve)

ax = plt.gca()

ax.plot(x,y,z,'o',color='r',markersize=10)

#ax.scatter(x,y,z,color='r',s=30)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

