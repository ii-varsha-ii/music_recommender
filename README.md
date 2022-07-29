# Music Recommendation Engine 
Music Recommendation &amp; Search Engine using content and collaborative based recommendation filtering techniques

A recommender system is a filtering system which aim is to predict a rating or preference a user
would give to an item, eg. a film, a product, a song, etc.

## Content-based filters:
Recommendations done using content-based recommenders can be seen as a
user-specific classification problem. This classifier learns the user's likes and dislikes
from the features of the song.

The idea behind is to extract meaningful keywords present in a song description a user
likes, search for the keywords in other song descriptions to estimate similarities among
them, and based on that, recommend those songs to the user.

Term Frequency-Inverse Document Frequency (TF-IDF) can be used for this matching
process since we deal with song lyrics/text here

### Phase 1:
Crawling and Scrapping:
This method takes in input a path to the directory that contains all the
html files crawled from AZlyrics and returns a dictionary for each html file

### Phase 2:
Indexing:
1. Generates Vocabulary and Inverted Index from json files.
2. Finds the tfidf values and cosine similarity table values

### Phase 3:
Ranking:
Rank the words based on the cosine-similarity values computed in the previous step
