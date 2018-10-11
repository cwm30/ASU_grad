
#source: http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC

import numpy as np
import matplotlib.pyplot as plt


X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
y = np.array([1, 1, 2, 2])
from sklearn.svm import SVC
clf = SVC(gamma='auto',kernel='linear')
clf.fit(X, y) 
SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
    decision_function_shape='ovr', degree=3, gamma='auto', kernel='rbf',
    max_iter=-1, probability=False, random_state=None, shrinking=True,
    tol=0.001, verbose=False)
print(clf.predict([[-0.8, -1]]))
print(clf.coef_)
a1,a2 = clf.coef_[0]

a = -a1/a2

xx = np.linspace(-3,3,50)

ys = xx*a - (clf.intercept_[0])/a2

px = X[:,0]
py = X[:,1]
print(px)
for i in range(0,y.shape[0]):
	print(i)
	if y[i] == 1:
		plt.plot(px[i],py[i],'ro')
	else:
		plt.plot(px[i],py[i],'b^')

plt.plot(-.8,-1,'rx')
plt.plot(xx,ys)
plt.show()
