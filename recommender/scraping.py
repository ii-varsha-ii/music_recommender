import glob
import json
import os
from bs4 import BeautifulSoup

from recommender.crawling import Crawling


class Scrapping:
    def __init__(self):
        self.crawler = Crawling()

    @staticmethod
    def html_to_json(path, az):
        # Generate one file JSON given the path of the file and the dictionary (az)
        path = path.split("\\")
        path.insert(1, "json")
        final_path = "//".join(path)
        final_path = final_path.replace(".html", ".json")
        with open(final_path, "w+") as file:
            json.dump(az, file)

    def __spin_crawler(self):
        return self.crawler.fetch_list_of_webpages()

    def save_details(self):
        db_table = []
        self.__spin_crawler()
        for filepath in glob.glob(os.path.join("../lyrics_collection/html", "*.html")):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f
                az = {}
                soup = BeautifulSoup(content, "html.parser")
                artists = soup.find_all("title")
                t = artists[0].text
                t = t.replace("| AZLyrics.com", "")
                t = t.split("-")
                az["artist"] = t[0]
                az["title"] = t[1]

                for br in soup.findAll("br"):
                    br.extract()
                lyrics = soup.find("div", {"class": "col-xs-12 col-lg-8 text-center"})
                if lyrics:
                    az["lyrics"] = lyrics.get_text(separator=" ")
                    az["lyrics"] = az["lyrics"].replace("\n", " ")
                    az["lyrics"] = az["lyrics"].replace("\r", " ")
                else:
                    continue
                az["url"] = filepath
                self.html_to_json(filepath, az)
                db_table.append(az)
        return self.crawler.save_data_to_file(db_table, "result.txt")
