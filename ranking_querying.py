import heapq
import json
import numpy
import time

from sklearn.cluster import KMeans

import indexing as ind


def toSearch(input, invertedInd, vocab):
    wordToFind = ind.wordNorm(input)
    IDs = []
    doclist = []
    for word in wordToFind:
        IDs.append(vocab[word])
    for id in IDs:
        doclist.extend(invertedInd[str(id)])
    return (doclist)


def text_in_vector(text_song, invIndex, vocab, json_name):
    word_vector = []
    text = ind.wordNorm(text_song)
    for v in vocab:
        if v in text:
            for (file, tf) in invIndex[str(vocab[v])]:
                if file == json_name:
                    word_vector.append(tf * ind.idf(invIndex, vocab[v]))
        else:
            word_vector.append(0)
    return (word_vector)


def makeQuery(input, vocab):
    query_vector = []
    wordToFind = ind.wordNorm(input)
    for v in vocab:
        if v in wordToFind:
            query_vector.append(1)
        else:
            query_vector.append(0)
    return (query_vector)


def get_cosine(vec1, vec2):
    vec_1 = numpy.array(vec1)
    vec_2 = numpy.array(vec2)

    numerator = sum(vec_1 * vec_2)
    sum1 = sum(numpy.power(vec_1, 2))
    sum2 = sum(numpy.power(vec_2, 2))
    denominator = numpy.sqrt(sum1) * numpy.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def unionQuery(query, invIndex, vocab):
    cosine = []
    q = ind.wordNorm(query)

    for x in q:
        searched = (toSearch(x, invIndex, vocab))
        vector_query = makeQuery(x, vocab)
        for (file, tf) in searched:
            song = ind.getText(file)
            tv = text_in_vector(song, invIndex, vocab, file)
            cosine.append([file, get_cosine(vector_query, tv)])
        heapq.heapify([cos for (file, cos) in cosine])
    return cosine[:10]


def getIntersection(query, invIndex, vocab):
    q = ind.wordNorm(query)
    doc = set(tup[0] for tup in toSearch(q[0], invIndex, vocab))
    for x in q:
        doc2 = toSearch(x, invIndex, vocab)
        doc = set([tup[0] for tup in doc2]) & doc
    return doc


def andQuery(query, k, index, v):
    cluster = []
    u = getIntersection(query, index, v)
    mergeddata = []

    for file in u:
        song = ind.getText(file)
        tv = text_in_vector(song, index, v, file)
        norm = numpy.linalg.norm(tv)
        tv_norm = [i / norm for i in tv]
        cluster.append(tv_norm)
    kmeans = KMeans(n_clusters=k, init='random')

    kmeans.fit(cluster)
    c = kmeans.predict(cluster)

    for row in range(0, len(cluster)):
        line = cluster[row]
        line.append(int(c[row]))
        mergeddata.append(line)
    text = ""
    for i in range(k):
        print("Cluster " + str(k))
        for file in u:
            song = ind.getText(file)
            text = text + str(song)
        text = ""
    return c



with open('vocab.json', 'r') as file:
    vocab = json.load(file)

with open('inverted_index.json', 'r') as file:
    index = json.load(file)

print(vocab)
print(index)
n = input('Type 0 for UNION query - Type 1 for AND query:')

if n == '0':
    query = input('Type query:')
    print('Searching query...')
    start_time = time.time()
    u = unionQuery(query, index, vocab)
    print(u)
    print('Execution Time:', (time.time() - start_time))
    for (value) in u:
        print('SCORE:', value)
elif n == '1':
    query = input('Type query:')
    k = input('Type number of cluster:')
    print('Searching query...')
    start_time = time.time()
    q = andQuery(query, int(k), index, vocab)
    print('Execution Time:', (time.time() - start_time))
    print(q)
else:
    print('INVALID CHOICE!')
