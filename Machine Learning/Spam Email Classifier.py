import re
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

from glob import glob
from nltk import PorterStemmer
from tqdm import tqdm_notebook

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from sklearn import svm
from sklearn.model_selection import train_test_split
from IPython.display import display_html

stemmer = PorterStemmer()
punct   = string.punctuation+"\r"+"\n"+"\ "
vocab   = np.array(open("data/vocab.txt").read().split())

def get_features(file):
    with open(file, encoding="cp437") as f:
        email = f.read()
        email = email.split("\n\n",1)[1]                        # handle email header
        email = email.lower()                                   # handle miscased words
        email = re.sub("<[^<>]+>",          " ",         email) # handle HTML tags
        email = re.sub("[0-9]+",            "number",    email) # handle numbers
        email = re.sub("http[s]?://[^\s]*", "httpaddr",  email) # handle URLs
        email = re.sub("[^\s]+@[^\s]+",     "emailaddr", email) # handle email addresses
        email = re.sub("[$]+",              "dollar",    email) # handle $ sign
        words = re.split("[{}]".format(punct),           email) # tokenize / remove punctuation

        token_email = []
        for word in words:
            word = re.sub("[^a-zA-Z0-9]", "", word)             # remove non-alpha characters
            word = word.strip()                                 # trim spaces
            word = stemmer.stem(word)                           # stem word
            if len(word) >= 1:                                  # ignore single characters
                token_email.append(word)
        return np.isin(vocab, token_email)

spam    = np.array([get_features(file) for file in tqdm_notebook(glob("data/spam/*"))])
notspam = np.array([get_features(file) for file in tqdm_notebook(glob("data/notspam/*"))])
X       = np.concatenate([spam, notspam])
y       = np.concatenate([np.ones(spam.shape[0]), np.zeros(notspam.shape[0])])

# SVM Train / Predict
X_train, X_test, y_train, y_test = train_test_split(X,      y,      test_size=0.3)
X_test,  X_val,  y_test,  y_val  = train_test_split(X_test, y_test, test_size=0.5)

model = svm.SVC(kernel='linear')
model.fit(X_train, y_train)  
accuracy = np.mean(model.predict(X_val) == y_val)

print("Cross Validation Accuracy: {:.0%} - Predictors:".format(accuracy))
pred = pd.DataFrame([*zip(vocab, model.coef_[0])], columns=["word", "weight"]).sort_values("weight")
html = pred.head(10).to_html(index=False) + pred.tail(10).to_html(index=False)
display_html(html.replace('table','table style="display:inline"'), raw=True)

Cross Validation Accuracy: 98% - Predictors:
WORD      WEIGHT
wrote     -0.974206
stuff     -0.965300
rpm       -0.911929
still     -0.856841
kill      -0.810159
instead   -0.716320
date      -0.687120
user      -0.656363
stock     -0.618307
around    -0.616337

WORD      WEIGHT
week      0.376939
basenumb  0.386184
below     0.397413
remov     0.429570
guarante  0.458399
tel       0.510011
bodi      0.531293
click     0.696832
our       0.764773
wi        0.900796

# PCA Dimensionality Reduction
def reduce_dim(feat, k):    
    feat   = np.matrix(feat)
    m      = feat.shape[0]
    norm   = feat - np.mean(feat)
    norm   = norm / np.std(norm)
    covmat = 1/m * (norm.T*norm)
    U,S,V  = np.linalg.svd(covmat) # PCA
    Z      = feat*U[:,1:k+1]
    approx = Z*U[:,1:k+1].T
    
#     error    = 1 - sum(S[:k+1]) / sum(S)
#     variance = 1 - np.mean(np.square((norm-approx))) / np.mean(np.square(norm))
#     print("{:.0%} variance retained.".format(error))
    
    model  = PCA(n_components=0.95, svd_solver="full")
    Z_sci  = model.fit_transform(StandardScaler().fit_transform(feat.astype(float)))
    retain = model.explained_variance_ratio_.cumsum()[-1]
    plt.title("Scree Plot - {:.2%} Retained with {}/{} PCs".format(retain, len(model.components_), m))
    plt.plot(model.explained_variance_ratio_)
    
    return Z, Z_sci, S

plt.figure(figsize=(12,8))
plt.subplot(221)
X_2d, X_2d_sci, S = reduce_dim(X_val, 2)
plt.subplot(222)
plt.scatter([X_2d_sci[:,0]], [X_2d_sci[:,1]])
plt.tight_layout()
