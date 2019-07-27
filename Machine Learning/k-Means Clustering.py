import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

def get_colors(container): # {0: (1,1,1,1)}
    cmap = {i:plt.get_cmap('gist_rainbow')(1.*i/k) for i in range(k)}
    return list(map(lambda x: cmap[x], container))

k     = 6
data  = pd.read_csv("data/kmeans.csv", header=None)
X     = np.array(data)
C     = np.array(data.loc[np.random.choice(data.index, size=k)])
x_idx = np.empty(X.shape[0])

history = []
for itr in range(10):
    for i in range(X.shape[0]): # Find Nearest Centroid
        x_idx[i] = np.argmin([sum((X[i] - C[j])**2) for j in range(C.shape[0])])

    history.append(C.tolist())
    
    for i in range(k): # Update Centroids
        C[i] = np.mean(X[x_idx == i], axis=0)

plt.figure(figsize=(5,4))
plt.title("Iterations: {}".format(10))
plt.scatter(*X.T, c=get_colors(x_idx), s=5,  marker="o")

for i, centroid in enumerate(map(lambda x: np.array(x).T, zip(*history))):
    plt.plot(*centroid, "-v", color=get_colors([i])[0], markeredgecolor="black")
plt.show()
