from nltk import SnowballStemmer, RegexpTokenizer
from nltk.corpus import stopwords
import enchant


def word_normalizer(text):
    # Text normalizer: split the text in array without all spaces, stopwords, numbers
    # Stemming all words, and return only the english words.
    stemmer = SnowballStemmer("english")
    new_text = []
    tokenizer = RegexpTokenizer(r"\w+")

    word_list = tokenizer.tokenize(text.lower())
    filtered_words_en = [
        word for word in word_list if word not in stopwords.words("english")
    ]
    stemming_words = [stemmer.stem(word) for word in filtered_words_en]
    d = enchant.Dict("en_US")
    for word in stemming_words:
        if not word.isdigit() and len(word) > 1 and d.check(word):
            new_text.append(word)
    return new_text
