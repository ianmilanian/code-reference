import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from sklearn.externals import joblib
%matplotlib inline

lda       = joblib.load("lda.pkl")
tweets    = joblib.load("tweets.pkl")
users     = open("users.txt",              encoding="utf-8").read().split()
keywords  = open("keywords.txt",           encoding="utf-8").read().split()
modifiers = open("keywords-modifiers.txt", encoding="utf-8").read().split() # indicator when matched with keywords

user_tweets    = pd.read_csv("user-tweets.txt", header=None, sep="|")[8].values
user_bow       = lda["vec"].transform(user_tweets)
user_transform = lda["lda"].transform(user_bow)
user_frame     = pd.DataFrame(user_transform)

ax = user_frame.plot(kind="bar", figsize=(15,15), colormap=cm.get_cmap('viridis'), stacked=True)
ax.get_xaxis().set_visible(False)
