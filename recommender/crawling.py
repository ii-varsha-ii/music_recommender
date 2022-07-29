import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.azlyrics.com/"


class Crawling:
    @staticmethod
    def get_all_artists(links):
        all_artist_links = []  # Link of all artists for each alphabet
        for link in links[:2]:
            time.sleep(1)
            req = requests.get(link)
            soup = BeautifulSoup(req.text, "html.parser")

            paging = soup.find_all("div", {"class": "col-sm-6 text-center artist-col"})
            for page in paging:
                all_artist_links += [
                    "/".join(link.split("/")[:-1]) + "/" + a["href"]
                    for a in page.find_all("a", href=True)
                ]

        return all_artist_links

    @staticmethod
    def get_all_song_links(all_artist_links):
        all_link_az = []
        for artist in all_artist_links[:2]:  # Link for each song for each artist
            time.sleep(1)
            url = artist
            req = requests.get(url)
            soup = BeautifulSoup(req.text, "html.parser")
            paging = soup.find_all("div", {"class": "listalbum-item"})
            for page in paging:
                all_link_az += [
                    "/".join(artist.split("/")[:-2])
                    + "/"
                    + "/".join(a["href"].split("/")[1:])
                    for a in page.find_all("a", href=True)
                ]
        return all_link_az

    @staticmethod
    def get_all_songs(links):
        webpage_htmls = {}
        for link in links[:20]:
            time.sleep(1)
            url = link
            req = requests.get(url)
            webpage_htmls[url] = BeautifulSoup(
                req.text, "html.parser"
            )  # html webpage for each song
        return webpage_htmls

    @staticmethod
    def save_to_file(webpage_htmls):
        for key, value in webpage_htmls.items():
            with open(
                "lyrics_collection/" + "_".join(key.rsplit("/", 2)[-2:]), "w+"
            ) as f1:
                f1.write(str(value.prettify()))

    @staticmethod
    def save_data_to_file(data, file_path):
        with open(file_path, "w+") as f1:
            f1.write(str(data))

    def fetch_list_of_webpages(self):
        req = requests.get(URL)
        soup = BeautifulSoup(req.text, "html.parser")

        paging = soup.find_all("div", {"class": "btn-group text-center"})

        links = [
            "https:" + a["href"] for a in paging[0].find_all("a", href=True)
        ]  # Link of each alphabet at the top header

        all_artist_links = self.get_all_artists(links)
        all_link_az = self.get_all_song_links(all_artist_links)
        webpage_htmls = self.get_all_songs(all_link_az)
        self.save_to_file(webpage_htmls)
        self.save_data_to_file(webpage_htmls, "webpages.txt")
