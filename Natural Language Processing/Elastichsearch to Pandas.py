import re
import json
import emoji
import requests
import pandas as pd

from tqdm import tqdm_notebook
from sklearn.externals import joblib
from elasticsearch import Elasticsearch, helpers

def clean_tweet(ret):
    ret = ret[2:] if ret[:2].lower() == 'rt' else ret                          # remove old retweet text
    ret = re.sub('[@][A-Za-z0-9_]+', ' ', ret)                                 # remove mentions
    ret = re.sub('[#]\S+',           ' ', ret)                                 # remove hashtags
    ret = re.sub('http[s]?://[A-Za-z\.\/0-9\-]+',  ' ', ret)                   # remove URLs
    ret = ret.replace('\n', ' ')                                               # remove newlines
    for symbol in open("symbols.txt").read(): ret = ret.replace(symbol, ' ');  # remove unwanted symbols
    ret = " ".join(re.sub("\s{1,100}", " ", ret).strip().split())              # remove multiple whiespaces
    ret = ret.lower().strip()                                                  # lowercase text
    return ret

docs  = []
url   = ""
es    = Elasticsearch(url, timeout=360)
query = { "query": json.loads(open("query.txt").read()) }
count = es.count(index="myindex", body=query)['count']
if count > 100000:
    raise RuntimeError("Query would return more than 100000 results.")
with tqdm_notebook(total=count) as pbar:
    for doc in helpers.scan(es, index="pulse", query=query, size=100):
        docs.append(doc["_source"]["doc"])
        pbar.update()
df = pd.DataFrame(docs)
tweets = [str(val).lower() for val in df["text"].values]
joblib.dump(tweets, "tweets.pkl")
