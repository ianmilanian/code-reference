import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

def feature_normalize(X, mu=None, sigma=None):
    mu     = mu if mu else np.mean(X)
    sigma  = sigma if sigma else np.std(X)
    X_norm = (X - mu) / sigma
    X_norm = np.insert(X_norm, 0, 1.0, axis=1)
    return X_norm, mu, sigma

def compute_cost(X, y, theta):
    m     = len(y)
    error = X*theta - y
    return error.T*error/(2*m)

def gradient_descent(X, y, theta, alpha, iters):
    m = len(y)
    J_history = np.zeros((iters, 1))
    for i in range(iters):
        theta = theta - alpha/m * (X.T*X*theta - X.T*y)
        J_history[i] = compute_cost(X, y, theta)
    return theta, J_history

def normal_equation(X, y):
    theta = (X.T*X).I*X.T*y
    return theta

# Load Data
data   = pd.read_csv('data/gradient/data.txt', header=None)
X      = np.matrix(data.iloc[:,0:2].values)
y      = np.matrix(data.iloc[:,2].values).T
theta  = np.zeros((3, 1))
alpha  = 0.01
iters  = 400

X_norm, mu, sigma = feature_normalize(X)
theta, J_history  = gradient_descent(X_norm, y, theta, alpha, iters)
theta2 = normal_equation(X_norm, y)

features      = [1650, 3]
features_norm = feature_normalize([features], mu, sigma)[0]

yhat    = X_norm*theta
yhat2   = X_norm*theta2
predict = (features_norm*theta).tolist()[0][0]
plt.figure(figsize=(12,8))
plt.subplot(221)
plt.scatter([X[:,0]], [y], c="b")
plt.plot(X[:,0], yhat, c="r")
plt.scatter(features[0], predict, c="g", s=70, zorder=10)
plt.title("{} sqft {}BR's - Price: ${:,.2f}".format(*features, predict))
plt.xlabel("Square Feet")
plt.ylabel("Price")

plt.subplot(222)
plt.plot(range(len(J_history)), J_history, c="b")
plt.title(r'J($\theta$) Cost')
plt.xlabel("Iterations")
plt.ylabel("Cost")
plt.tight_layout()
