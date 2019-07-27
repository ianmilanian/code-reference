import nltk
import numpy as np

from matplotlib import cm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
%matplotlib inline

# Simple Sentiment Scoring (English)
neg_words = set(open("../data/negative.txt").read().split())
pos_words = set(open("../data/positive.txt").read().split())
tk_tweets = nltk.Text(nltk.TweetTokenizer().tokenize("".join(tweets)))
tweet_fd  = nltk.FreqDist(tk_tweets)

tweet_hapaxes = tweet_fd.hapaxes()
tweet_fd.plot(15, cumulative=True)
tweet_fd.tabulate(15, cumulative=True)

print("\nHapaxes:", " ".join(tweet_hapaxes[:5]), "...")

similar_word = "trump"
print("\nWords Near {}:".format(similar_word))
tk_tweets.similar(similar_word)

print("\nCollocations:")
tk_tweets.collocations()

count = 0
for tweet in tweets:
    words     = tweet.split()
    sentiment = tweet, len(pos_words.intersection(words)), len(neg_words.intersection(words))
    print(tweet)
    count += 1
    if count > 20:
        break

print("\nTweet Sentiment:", sentiment)

freq     = 125
df_tags  = pd.DataFrame(nltk.pos_tag(tk_tweets), columns=["word", "grammar"])
df_nouns = df_tags[(df_tags["grammar"] == "NN") & (df_tags["word"].str.len() > 1)]["word"].value_counts()
df_nouns = df_nouns[df_nouns[:,] > freq]
df_nouns.plot.pie(title="Tweeted Nouns With %d+ Occurances" % freq, figsize=(12,12), colormap=cm.get_cmap('viridis'))

# Sentiment Analysis with VADER
vader  = SentimentIntensityAnalyzer()
vscore = [vader.polarity_scores(tweet) for tweet in tweets]
np.mean([score["neutral"] for score in vscore])
