from textblob import TextBlob
from nltk.corpus import stopwords as nltk_stopwords
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def generate_topics(lda, vec, n):
    topics   = []
    features = vec.get_feature_names()
    for i, topic in enumerate(lda.components_):
        topic_words = []
        for j in topic.argsort()[:-n-1:-1]: #last n topic words
            try:
                topic_words.append(str(TextBlob(features[j]).translate(to="en")))
            except:
                topic_words.append(features[j])
                pass
        topics.append("Topic {}: {}".format(i+1, " ".join(topic_words)))
    return topics

tweets = joblib.load("tweets.pkl")
stopwords = set(nltk_stopwords.words("english") + ["rt", "http", "https", "co"])
vec = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words=stopwords)
bow = vec.fit_transform(tweets)
lda = LatentDirichletAllocation(
    n_topics=10,
    max_iter=5,
    learning_method='online',
    learning_offset=50.,
    random_state=0).fit(bow)

joblib.dump({"topics":generate_topics(lda, vec, 10), "vec":vec, "bow":bow, "lda":lda}, "lda.pkl", compress=True)
