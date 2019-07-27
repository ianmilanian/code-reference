import cv2
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from skimage import feature
from skimage import exposure
from sklearn.externals import joblib
%matplotlib inline

# Model trained on CIFAR-10 Dataset

Xtr, Ytr, Xte, Yte, classes = joblib.load("data/cifar-10.pkl")

def svm_predict(X, theta):
    return np.argmax(X.dot(theta), axis=1)
    
def svm_loss(X, theta, y, reg, delta=1.0):
    minbatch = np.random.choice(X.shape[0], 200)
    X        = X[minbatch]
    y        = y[minbatch]
    n, dim   = X.shape
    scores   = X.dot(theta)
    correct  = scores[np.arange(n), y][:, np.newaxis]
    margins  = np.maximum(0, scores - correct + delta)
    margins[np.arange(n), y] = 0
    loss     = np.mean(margins)*dim + reg*np.sum(np.square(theta))
    mask     = margins > 0
    grad     = X.T.dot(mask) / n + reg * theta
    return loss, grad

def svm_train(X, y, alpha, reg, iterations):
    history = []
    n, dim  = X.shape
    classes = np.max(y) + 1  # y takes values 0...K-1
    theta   = 0.001 * np.random.randn(dim, classes)
    for _ in range(iterations):
        loss, grad = svm_loss(X, theta, y, reg)
        history.append(loss)
        theta += -alpha * grad # update
    return theta, history

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

X = Xtr_features
y = Ytr
model = {"alpha": None, "lambda": None, "theta": None, "history": None, "accuracy": 0}
for alpha in [1e-9, 1e-8, 1e-7]:
    for reg in [5e4, 5e5, 5e6]:
        theta, history = svm_train(X, y, alpha, reg, 1500)
        predict  = svm_predict(X, theta)
        accuracy = np.mean(predict == y)
        if accuracy > model["accuracy"]:
            model = {"alpha": alpha, "lambda": reg, "theta": theta, "history": history, "accuracy": accuracy}

predict  = svm_predict(Xte_features, model["theta"])
accuracy = np.mean(predict == Yte)
plt.plot(model["history"])
plt.xlabel("Iterations")
plt.ylabel(r"J($\theta$) Cost")
plt.title("Accuracy: {:.2%}".format(accuracy))

# Accuracy: 39.20%
