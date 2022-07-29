import codecs
import heapq
import json
import math

import numpy
import time

from sklearn.cluster import KMeans

from recommender.utils import word_normalizer


class Ranking:
    def __init__(self):
        self.json_dir = "lyrics_collection//json//"

    @staticmethod
    def compute_idf(inv_index, k):
        idf = math.log((10 / len(inv_index[str(k)])))
        return idf

    def get_text(self, file):
        counter = 0
        d = json.loads(
            codecs.open(self.json_dir + file, "r", encoding="ISO-8859-1").read()
        )
        counter += 1
        txt = d["lyrics"]
        return txt

    def to_search(self, word, invertedInd, vocab):
        wordToFind = word_normalizer(word)
        IDs = []
        doclist = []
        for word in wordToFind:
            IDs.append(vocab[word])
        for id in IDs:
            doclist.extend(invertedInd[str(id)])
        return doclist

    def text_in_vector(self, text_song, invIndex, vocab, json_name):
        word_vector = []
        text = word_normalizer(text_song)
        for v in vocab:
            if v in text:
                for (file, tf) in invIndex[str(vocab[v])]:
                    if file == json_name:
                        word_vector.append(tf * self.compute_idf(invIndex, vocab[v]))
            else:
                word_vector.append(0)
        return word_vector

    def make_query(self, word, vocab):
        query_vector = []
        wordToFind = word_normalizer(word)
        for v in vocab:
            if v in wordToFind:
                query_vector.append(1)
            else:
                query_vector.append(0)
        return query_vector

    @staticmethod
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

    def union_query(self, query, inv_index, vocab):
        cosine = []
        q = word_normalizer(query)

        for x in q:
            searched = self.to_search(x, inv_index, vocab)
            vector_query = self.make_query(x, vocab)
            for (file, tf) in searched:
                song = self.get_text(file)
                tv = self.text_in_vector(song, inv_index, vocab, file)
                cosine.append([file, self.get_cosine(vector_query, tv)])
            heapq.heapify([cos for (file, cos) in cosine])
        return cosine[:10]

    def get_intersection(self, query, inv_index, vocab):
        q = word_normalizer(query)
        doc = set(tup[0] for tup in self.to_search(q[0], inv_index, vocab))
        for x in q:
            doc2 = self.to_search(x, inv_index, vocab)
            doc = set([tup[0] for tup in doc2]) & doc
        return doc

    def and_query(self, query, k, index, v):
        cluster = []
        u = self.get_intersection(query, index, v)
        mergeddata = []

        for _ in u:
            song = self.get_text(_)
            tv = self.text_in_vector(song, index, v, _)
            norm = numpy.linalg.norm(tv)
            tv_norm = [i / norm for i in tv]
            cluster.append(tv_norm)
        kmeans = KMeans(n_clusters=k, init="random")

        kmeans.fit(cluster)
        c = kmeans.predict(cluster)

        for row in range(0, len(cluster)):
            line = cluster[row]
            line.append(int(c[row]))
            mergeddata.append(line)
        text = ""
        for i in range(k):
            print("Cluster " + str(k))
            for _ in u:
                song = self.get_text(_)
                text = text + str(song)
            text = ""
        return c

    def orchestrator(self, choice, inv_index, vocab):
        if choice == "0":
            query = input("Type query:")
            print("Searching query...")
            start_time = time.time()
            u = self.union_query(query, inv_index, vocab)
            print(u)
            print("Execution Time:", (time.time() - start_time))
            for value in u:
                print("SCORE:", value)
        elif choice == "1":
            query = input("Type query:")
            k = input("Type number of cluster:")
            print("Searching query...")
            start_time = time.time()
            q = self.and_query(query, int(k), inv_index, vocab)
            print("Execution Time:", (time.time() - start_time))
            print(q)
        else:
            print("INVALID CHOICE!")
