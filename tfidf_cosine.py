import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
songs = pd.read_csv('song_dataset.csv')
#songs = songs.sample(n=5000).drop('link', axis=1).reset_index(drop=True)
#songs['text'] = songs['text'].str.replace(r'\n', '')
tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
lyrics_matrix = tfidf.fit_transform(songs['lyrics'])
cosine_similarities = cosine_similarity(lyrics_matrix)
similarities = {}

print(lyrics_matrix)
