import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib
%matplotlib inline

# Model trained on CIFAR-10 Dataset

Xtr, Ytr, Xte, Yte, classes = joblib.load("data/cifar-10.pkl")

# Truncate Dataset
Xtr = Xtr[:5000]
Ytr = Ytr[:5000]
Xte = Xte[:5000]
Yte = Yte[:5000]

# Reshape image data into rows
Xtr_features = np.reshape(Xtr, (Xtr.shape[0], -1))
Xte_features = np.reshape(Xte, (Xte.shape[0], -1))

# Calculate distance (vectorized) -> (p-q)^2 = p^2 + q^2 - 2pq
p  = np.sum(Xte_features**2, axis=1, keepdims=True)
q  = np.sum(Xtr_features**2, axis=1)
pq = np.dot(Xte_features, Xtr_features.T)
dist = np.sqrt(p + q - 2*pq)

# Find k-NN and predict label
k = 5
n = dist.shape[0]
Ypr = np.zeros(n)
for i in range(n):
    closest_y = Ytr[np.argsort(dist[i,:])[0:k]] # k closest images
    Ypr[i] = np.argmax(np.bincount(closest_y))
predict = Ypr == Yte
print("{}/{} correct => accuracy: {:.0%}".format(np.sum(predict), n, np.mean(predict)))

plt.figure(figsize=(10,10))
for i in range(1,16):
    plt.subplot(5, 5, i)
    plt.title("guessed {} ({})".format(classes[Ypr[i].astype("int")], classes[Yte[i].astype("int")]))
    plt.imshow(Xte[i].astype('uint8'))
    plt.axis('off')
plt.tight_layout()
plt.show()

# 1336/5000 correct => accuracy: 27%
