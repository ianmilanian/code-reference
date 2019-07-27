import numpy as np
import pandas as pd
import scipy.optimize as op
import matplotlib.pyplot as plt
%matplotlib inline

def map_feature(x1, x2):
    '''
    Maps the two input features to quadratic features.
    Returns a new feature array with more features, comprising of
    X1, X2, X1 ** 2, X2 ** 2, X1*X2, X1*X2 ** 2, etc...
    Inputs X1, X2 must be the same size
    '''
    x1.shape = (x1.size, 1)
    x2.shape = (x2.size, 1)
    degree = 6
    out = np.ones(shape=(x1[:, 0].size, 1))
    
    m, n = out.shape
    for i in range(1, degree+1):
        for j in range(i+1):
            r = (x1 ** (i - j)) * (x2 ** j)
            out = np.append(out, r, axis=1)
    return out

def decision_boundary(theta):
    u = np.linspace(-1, 1.5, 50)
    v = np.linspace(-1, 1.5, 50)
    z = np.zeros(shape=(len(u), len(v)))
    for i in range(len(u)):
        for j in range(len(v)):
            z[i, j] = (map_feature(np.array(u[i]), np.array(v[j])).dot(theta.T))
    z = z.T
    return u, v, z

def sigmoid(h):
    return 1/(1 + np.exp(-h))

def predict(theta, X):
    theta = np.matrix(theta).T
    p = sigmoid(X*theta)
    p[p >= 0.5] = 1
    p[p <  0.5] = 0
    return p

def compute_cost(theta, X, y, reg):
    theta = np.matrix(theta).T
    shift = theta.copy()
    shift[0] = 0
    m = len(y)
    h = sigmoid(X*theta)
    J = 1/m*(-y.T*np.log(h) - (1-y).T*np.log(1-h)) + (reg/(2*m)*shift.T*shift)
    grad = 1/m*(X.T*h - X.T*y) + (1/m*reg*shift)
    return J, grad

# Load Data
X = np.matrix(pd.read_csv('data/regression/x.txt', header=None).values)
y = np.matrix(pd.read_csv('data/regression/y.txt', header=None).values)

plt.figure(figsize=(12,8))
for i, reg in enumerate([0, 1]):
    theta  = np.ones((X.shape[1], 1))
    result = op.minimize(
                fun     = compute_cost,
                x0      = theta,
                args    = (X, y, reg),
                method  = 'TNC',
                jac     = True,
                options = {'maxiter': 4000})

    theta = result.x
    data  = np.array(np.append(X[:,1:3], y, axis=1))
    pos   = data[data[:,2] == True ][:,0:2]
    neg   = data[data[:,2] == False][:,0:2]
    
    plt.subplot(int(str(22)+str(i+1)))
    plt.scatter([pos[:,0]], pos[:,1], marker="+", c="black",  edgecolors="black")
    plt.scatter([neg[:,0]], neg[:,1], marker="o", c="yellow", edgecolors="black")
    plt.contour(*decision_boundary(theta), levels=[0], colors="red")
    accuracy = y[predict(theta, X)==y].size/y.size*100.0
    plt.title('Accuracy: {:.2f}% - Lambda: {}'.format(accuracy, reg))
    plt.legend(['y = True', 'y = False', 'Decision boundary'])
plt.tight_layout()
