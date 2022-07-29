from recommender.builder import Builder
from recommender.indexing import Indexer
from recommender.ranking import Ranking
from recommender.scraping import Scrapping


class MusicRecommendationEngine:
    def __init__(self):
        self.builder = Builder()
        self.scrapping = Scrapping()
        self.indexing = Indexer()
        self.ranking = Ranking()

    def start(self):
        choice = input("Type 0 for UNION query - Type 1 for AND query:")
        print("::Build the songs dataset::")
        self.builder.build_public_tracks_dataset()
        print("::Build the users dataset::")
        self.builder.build_user_tracks_dataset()
        self.scrapping.save_details()
        vocab, inv_index = self.indexing.compute_inverted_indices()
        return self.ranking.orchestrator(choice, inv_index, vocab)
