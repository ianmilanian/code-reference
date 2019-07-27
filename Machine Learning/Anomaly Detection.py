
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

'''
Multivariate Guassian Model:
Very small positive number of examples (skewed data).
Many different types of anomalies. Hard for an algorithm to learn from positive examples alone.
Good for things like fraud detection and monitoring data center machines.
Accuracy is not a good measure of performance for Anomaly Detection (skewed data) use something like F1-Score.
Multivariate Guassian model is computationally more expensive than the normal model, but captures correlations between features.
Try getting features close to gaussian via transformation.
Prefer supervised learning algorithms like Linear Regression when large number of positive/negative examples.
Prefer using a normal Guassian model when sigma is non-invertible. Highly redudant features might make sigma non-invertible.
'''

def build_contour(mu, sig2):
    x1, x2 = np.meshgrid(np.arange(0, 35.5, 0.5), np.arange(0, 35.5, 0.5))
    Z = multivariate_guassian(np.vstack((x1.flatten(), x2.flatten())).T, mu, sig2)
    Z = np.reshape(Z, (x1.shape[0], x2.shape[0]))
    plt.contour(x1, x2, Z, 10**np.arange(-20, 0, 3).astype(float))

def select_threshold(p, yval):
    best = (0,0)
    step = (np.max(p) - np.min(p)) / 1000
    for epsilon in np.arange(np.min(p), np.max(p), step):
        tp   = np.sum((p < epsilon) & (yval == 1))
        fp   = np.sum((p < epsilon) & (yval == 0))
        fn   = np.sum((p > epsilon) & (yval == 1))
        prec = tp / (tp + fp)        if (tp + fp)  else 0 # divide by zero guard
        rec  = tp / (tp + fn)        if (tp + fn)  else 0 # divide by zero guard
        f1   = 2*prec*rec/(prec+rec) if (prec+rec) else 0 # divide by zero guard
        if (f1 > best[0]):
            best = (f1, epsilon)
    return best

def multivariate_guassian(X, mu, sig2):
    k    = len(mu)+1
    X_mu = X-mu
    sig2 = np.matrix(np.diag(sig2.A1))
    norm = (2*np.pi)**(-k/2)*np.power(np.linalg.det(sig2), -0.5)
    return norm * np.exp(-0.5*np.sum(np.multiply(X_mu*sig2.I,X_mu), axis=1))

def estimate_guassian(X):
    mu   = np.mean(X, axis=0)
    sig2 = np.mean(np.square(X-mu), axis=0)
    return mu, sig2

X    = np.matrix(np.genfromtxt("data/anomaly/X.csv",    delimiter=','))
Xval = np.matrix(np.genfromtxt("data/anomaly/Xval.csv", delimiter=','))
yval = np.matrix(np.genfromtxt("data/anomaly/yval.csv", delimiter=',')).T

mu, sig2 = estimate_guassian(X)
p = multivariate_guassian(X, mu, sig2)
f1, epsilon = select_threshold(p, yval)

plt.figure(figsize=(7,5))
build_contour(mu, sig2)
plt.scatter([X[:,0]], [X[:,1]], marker="x")
plt.title("Epsilon - {:.2%}".format(epsilon))
plt.xlabel("Latency (ms)")
plt.ylabel("Throughput (mb/s)")
plt.scatter([X[:,0][p < epsilon]], [X[:,1][p < epsilon]], s=100, facecolors='none', edgecolors='r')
