import spotipy
import pandas as pd
import numpy as np
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import json
import requests
from bs4 import BeautifulSoup
from musixmatch import Musixmatch


class Builder:
    def __init__(self):
        self.credentials = json.load(open("../resources/authorization.json"))
        self.GENIUS_URL = "http://genius.com/"

    def __get_credentials(self) -> Spotify:
        client_id = self.credentials["client_id"]
        client_secret = self.credentials["client_secret"]
        genius_key = self.credentials["genius_key"]
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        token = client_credentials_manager.get_access_token()
        return Spotify(auth=token)

    def __get_user_credentials(self):
        client_id = self.credentials["client_id"]
        client_secret = self.credentials["client_secret"]
        user_id = self.credentials["user_id"]
        token = spotipy.util.prompt_for_user_token(
            user_id,
            "user-top-read",
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8000",
        )
        sp2 = spotipy.Spotify(auth=token)
        sp2.trace = False
        return sp2

    @staticmethod
    def add_to_dataset(track_info, filename) -> None:
        df = pd.DataFrame(
            np.array(track_info),
            columns=["song_id", "artist", "song", "lyrics", "features"],
        )

        df[
            [
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
            ]
        ] = pd.DataFrame(df.features.to_list(), index=df.index)
        df = df.drop(columns=["features"])
        df.to_csv(filename, index=False)

    def fetch_lyrics_from_genius(self, artist, song):
        song_url = "{}-{}-lyrics".format(
            str(artist).strip().replace(" ", "-"), str(song).strip().replace(" ", "-")
        )

        request = requests.get(f"{self.GENIUS_URL}{song_url}")

        if request.status_code == 200:
            html_code = BeautifulSoup(request.text, features="html.parser")
            lyrics1 = html_code.find("div", class_="lyrics")
            lyrics2 = html_code.find(
                "div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn"
            )
            if lyrics1:
                return lyrics1.get_text()
            elif lyrics2:
                return lyrics2.get_text()
            elif lyrics1 == lyrics2 is None:
                return None

    def fetch_lyrics_from_musixmatch(self, artist, others, song):
        musixmatch_key = self.credentials["musixmatch_key"]

        if others is not None:
            artist_details = artist + " feat " + others
        else:
            artist_details = artist
        mus = Musixmatch(musixmatch_key)
        response = mus.matcher_lyrics_get(q_track=song, q_artist=artist_details)

        if len(response["message"]["body"]) != 0:
            print(response["message"]["body"]["lyrics"]["lyrics_body"])
            return response["message"]["body"]["lyrics"]["lyrics_body"]
        return None

    def build_public_tracks_dataset(self):
        client = self.__get_credentials()
        playlist_link = self.credentials["public_tracks_playlist"]
        results = client.playlist(playlist_link)
        songs = results["tracks"]["items"]

        track_info = []
        for idx, item in enumerate(songs):
            track = item["track"]
            artist = track["artists"][0]["name"]
            song = track["name"]
            song = song.split("(")[0].strip()
            print(
                idx,
                track["artists"][0]["name"],
                "//",
                track["artists"][1]["name"],
                "-",
                track["name"],
            )
            lyrics = self.fetch_lyrics_from_musixmatch(artist, None, song)
            if lyrics is not None:
                lyrics = lyrics.replace("\n", " ")
            track_info.append([track["id"], artist, song, lyrics.strip("\n")])
        self.add_to_dataset(track_info, "../resources/data/song_dataset.csv")

    def build_user_tracks_dataset(self):
        client = self.__get_user_credentials()
        track_info = []
        results = client.current_user_top_tracks(limit=100)
        for i, item in enumerate(results["items"]):
            song = item["name"]
            song = song.split("(")[0].strip()
            artist = item["artists"][0]["name"]
            id = item["id"]
            if len(item["artists"]) > 1:
                others = item["artists"][1]["name"]
            else:
                others = None
            print(i, item["name"], "//", item["artists"][0]["name"])

            lyrics = self.fetch_lyrics_from_musixmatch(artist, others, song)
            if lyrics is None:
                print("passing ", artist, "-", song)
                continue
            lyrics = lyrics.replace("\n", " ")
            lyrics = lyrics.replace(
                "******* This Lyrics is NOT for Commercial use *******", ""
            )
            features = client.audio_features(id)
            features = self.construct_features(features[0])
            print(features[:11])
            track_info.append(
                [item["id"], artist, song, lyrics.strip("\n"), features[:11]]
            )
        print(track_info)
        self.add_to_dataset(track_info, "../resources/data/user_dataset.csv")

    @staticmethod
    def construct_features(features):
        result = []
        for key in features:
            result.append(features[key])
        return result
