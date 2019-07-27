import re
import string
import matplotlib.pyplot as plt

from scipy.misc import imread
from wordcloud import WordCloud

from textblob import TextBlob
from textblob.exceptions import NotTranslated
from nltk.corpus import stopwords as nltk_stopwords

def clean_text(text):
    if text:
        stop = set(nltk_stopwords.words("english") + ["&amp;", "&gt;", "rt"])
        punc = string.punctuation + u"\u2026" + u"\ud83d" + u"\ud83c" + "\n"
        text = text.lower()                                                #remove case (duplicates)
        text = re.sub("http[s]?://[A-Za-z\.\/0-9\-]+", " ", text)          #remove URLs
        for symbol in punc: text = text.replace(symbol, " ");              #remove puncuation
        for word in stop: text = re.sub(r"\b{}\b".format(word), " ", text) #remove stopwords
        text = " ".join(re.sub("\s{1,100}", " ", text).strip().split())    #remove multiple white spaces
    return text

def translate_text(text, lang):
    response = text
    try:
        response = str(TextBlob(text).translate(to=lang))
    except NotTranslated:
        pass
    except Exception as e:
        print(e)
    return response

def get_wordcloud(mask_path=None):
    cloud = WordCloud(
        width        = 1920,
        height       = 1080,
        font_path    = "data/arial.ttf",
        max_words    = 500,
        mask         = imread(mask_path) if mask_path else None,
        random_state = 42,
        colormap     = plt.get_cmap("GnBu"))
    return cloud

def save_wordcloud(cloud, path):
    plt.figure(figsize=(26.6,15), facecolor='k')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.imshow(cloud, interpolation="bilinear")
    plt.savefig(path, facecolor='k', bbox_inches='tight')
    plt.close('all')

def generate_wordcloud(words, path, mask_path):
    cloud = get_wordcloud(mask_path)
    cloud.generate(words)
    save_wordcloud(cloud, path)
