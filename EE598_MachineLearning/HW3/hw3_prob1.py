import numpy.linalg as linalg
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# fig = plt.figure()
# ax = fig.add_subplot(111,projection='3d')



data = [[2,3],[3,4],[4,5]]
ans = [5,6,7]


a,b = linalg.lstsq(data,ans)[0]
error = linalg.lstsq(data,ans)[1]
print(a,b,error)
arr = np.asarray(data)
x = arr[:,0]
y = arr[:,1]

#plane ax + by +cz +d =0
xx, yy = np.meshgrid(range(5),range(2,6))
p1 = np.array([data[0][1],data[0][1],ans[0]])
n1 = np.array([a,b,-1])

d = -p1.dot(n1)
d=0
print(d)
z = (-n1[0]*xx-n1[1]*yy -d)*1./n1[2]




plt3d = plt.figure().gca(projection='3d')
plt3d.plot_surface(xx,yy,z,color="lightgrey")
#plt3d.plot(x,y,ans,'o',color='r')
ax = plt.gca()
ax.scatter(x,y,ans,'o',color='r',s=40)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

# plt.plot(x,arr[:,1],'o', label="data", markersize=5)
# plt.plot(x, m*x + c*y, 'r', label="fitted line")
# plt.legend()
# plt.show()
