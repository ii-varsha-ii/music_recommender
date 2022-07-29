import os.path
import json
import codecs

from recommender.utils import word_normalizer


class Indexer:
    def __init__(self):
        self.json_dir = "lyrics_collection//json//"

    def all_words(self):
        # This function returns in an array all the words of all lyrics (saved as JSON file)
        k = []
        count = 0
        for file in os.listdir(self.json_dir):
            d = json.loads(
                codecs.open(self.json_dir + file, "r", encoding="ISO-8859-1").read()
            )
            count += 1
            word_list = word_normalizer(d["lyrics"])
            for item in word_list:
                k.append(item)
            print(count, "---> JSON IN VOCABULARY")
        return k

    @staticmethod
    def save_data_to_file(data, file):
        file = open(file, "w+")
        json.dump(data, file)

    def create_vocab(self, all_words):
        # This function take in input an array with all words, create the set and assign an ID to each term
        # vocabulary = {term : termID}
        vocabulary = {}
        word_list = sorted(list(set(all_words)))
        for ID, elem in enumerate(word_list):
            vocabulary.update({elem: ID})
        self.save_data_to_file(vocabulary, "../resources/data/vocab.json")
        return vocabulary

    @staticmethod
    def term_freq(term, txt):
        # Compute the term frequencies in a given text
        count = 0
        if len(txt) <= 0:
            return 0
        else:
            for t in txt:
                if t == term:
                    count += 1
            return count / len(txt)

    def inverted_index(self, vocab):
        # invIndex = {termID : (doc, TF)}
        inv_index = {}
        counter = 0
        for file in os.listdir(self.json_dir):
            try:
                d = json.loads(
                    codecs.open(self.json_dir + file, "r", encoding="ISO-8859-1").read()
                )
                counter += 1
                txt = word_normalizer(d["lyrics"])
                for word in vocab:
                    tf = self.term_freq(word, txt)
                    if tf > 0:
                        try:
                            inv_index[vocab[word]] += [(file, tf)]
                        except:
                            inv_index[vocab[word]] = [(file, tf)]

                print(counter, "----->IN INVERTED INDEX!")
            except:
                print("!!!!!!!!!!!IN EXCEPT", file)
                pass
        self.save_data_to_file(inv_index, "../resources/data/inverted_index.json")
        return inv_index

    def compute_inverted_indices(self):
        all_words = self.all_words()
        vocabularies = self.create_vocab(all_words)
        inv_indices = self.inverted_index(vocabularies)
        return vocabularies, inv_indices
