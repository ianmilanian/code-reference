import cv2
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm_notebook
from skimage import feature
from skimage import exposure
from sklearn.externals import joblib
%matplotlib inline

# Model trained on CIFAR-10 Dataset

Xtr, Ytr, Xte, Yte, classes = joblib.load("data/cifar-10.pkl")

def extract_features(images):
    feature_vec = []
    for im in images:
        # color histogram
        hsv = matplotlib.colors.rgb_to_hsv(im/255)*255
        hist, bin_edges = np.histogram(hsv[:,:,0], bins=np.linspace(0, 255, 10+1), density=True) # normalized
        hist = hist * np.diff(bin_edges)

        # hog descriptors
        im = im[:,:,0] if im.ndim == 3 else np.at_least_2d(im) # grayscale
        h  = feature.hog(im, pixels_per_cell=(8,8), cells_per_block=(4,4))
        feature_vec.append(np.concatenate((h,hist)))
    return np.array(feature_vec)

Xtr_features = extract_features(Xtr)
Xte_features = extract_features(Xte)

# Apply mean normalization to features
mu  = np.mean(Xtr_features, axis=0)
std = np.std(Xtr_features,  axis=0)
Xtr_features = (Xtr_features-mu)/std
Xte_features = (Xte_features-mu)/std

# Add bias unit
Xtr_features = np.hstack([Xtr_features, np.ones((Xtr_features.shape[0], 1))])
Xte_features = np.hstack([Xte_features, np.ones((Xte_features.shape[0], 1))])

"""
Network Architecture:
input - fully connected layer - ReLU - fully connected layer - softmax
"""

def nn_init(fin, fout): # Xavier/2
    return np.random.randn(fin, fout) / np.sqrt(fin/2)

def nn_update(weights, grad, momentum, step, alpha, beta1=0.9, beta2=0.95): # Adam Update (ADAGRAD + Momentum)
    update = []
    m, v = momentum
    for x, dx in zip(weights, grad):
        m = beta1*m + (1-beta1)*(dx)
        v = beta2*v + (1-beta2)*(dx**2)
        m = m / (1-beta1)**step
        v = v / (1-beta2)**step
        update.append(x - alpha * m / (np.sqrt(v) + 1e-7))
    return update, [m,v]

def nn_predict(X, weights):
    w1,b1,w2,b2 = weights    
    hidden = np.maximum(0, np.dot(X, w1) + b1) # ReLU nonlinearity
    output = np.dot(hidden, w2) + b2
    return np.argmax(output, axis=1)

def nn_iteration(X, y, weights, alpha, reg, p=0.5):
    w1,b1,w2,b2 = weights
    
    # Forward Pass
    n      = X.shape[0]
    hidden = np.maximum(0, np.dot(X, w1) + b1)                   # ReLU nonlinearity activation
    hidden = hidden * ((np.random.randn(*hidden.shape) < p) / p) # Regularization dropout
    output = np.dot(hidden, w2) + b2
    
    p = np.exp(output)
    p = p / np.sum(p, axis=1, keepdims=True) # normalize
    J = np.sum(-np.log(p[range(n),y]))/n + reg*np.sum(w1*w1) + reg*np.sum(w2*w2)
    
    # Backward Pass
    dscores = p
    dscores[range(n), y] -= 1
    dscores /= n
    
    dw2 = np.dot(hidden.T, dscores) + reg*w2
    db2 = np.sum(dscores, axis=0)
    dhidden = np.dot(dscores, w2.T)
    dhidden[hidden <= 0] = 0
    dw1 = np.dot(X.T, dhidden) + reg*w1
    db1 = np.sum(dhidden, axis=0)
    
    return J, [dw1,db1,dw2,db2]

def nn_train(X, y, batch_size=200, layers=500, decay=0.95, alpha=1e-3, reg=1e-5, iterations=1000):
    n, dim = X.shape
    output = np.max(y)+1
    w1 = nn_init(dim, layers)
    w2 = nn_init(layers, output)
    b1 = np.zeros(layers)
    b2 = np.zeros(output)
    weights = [w1,b1,w2,b2]
    
    history    = []
    momentum   = [0, 0]
    epoch_size = n/batch_size
    for step in range(iterations):
        batch   = np.random.choice(n, batch_size)
        J, grad = nn_iteration(X[batch], y[batch], weights, alpha, reg)
        
        #weights, momentum = nn_update(weights, grad, momentum, step, alpha)
        
        weights = [i-alpha*j for i,j in zip(weights, grad)] #update SGD
        
        if step % epoch_size == 0:
            alpha = alpha*decay
            # ensemble weights average
            # x_test = 0.995*x_test + 0.005*x
        history.append(J)        
    return weights, history

X = Xtr_features
y = Ytr

weights, history = nn_train(X, y, alpha=1.0, reg=0.0)

# model = {"alpha": None, "lambda": None, "weights": None, "history": None, "accuracy": 0}
# for _ in tqdm_notebook(range(100)): # hyperparam optimiziation, sample logspace for alpha/reg
#     weights, history = nn_train(X, y, alpha=10**np.random.uniform(-5,5), reg=10**np.random.uniform(-3,6))
#     predict  = nn_predict(X, weights)
#     accuracy = np.mean(predict == y)
#     if accuracy > model["accuracy"]:
#         model = {"alpha": alpha, "lambda": reg, "weights": weights, "history": history, "accuracy": accuracy}

# im   = [cv2.resize(cv2.imread("data/kmeans_tiger.jpg"), (32, 32))]
# feat = extract_features(im)
# feat = (feat-mu)/std
# feat = np.hstack([feat, np.ones((feat.shape[0], 1))])
# predict = nn_predict(feat, model["weights"])
# print("Predicted Class: {} (test)".format(predict[0]))

# predict  = nn_predict(Xte_features, model["weights"])
# accuracy = np.mean(predict == Yte)
# print(accuracy)
# plt.plot(model["history"])

predict  = nn_predict(Xte_features, weights)
accuracy = np.mean(predict == Yte)
plt.plot(history)
plt.xlabel("Iterations")
plt.ylabel(r"J($\theta$) Cost")
plt.title("Accuracy: {:.2%}".format(accuracy))

# Accuracy: 57.05%
