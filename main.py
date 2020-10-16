import spotipy
import pandas as pd
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import json
import requests
from bs4 import BeautifulSoup
from musixmatch import Musixmatch


def add_to_dataset(track_info, filename):
    df = pd.DataFrame(np.array(track_info), columns=['song_id', 'artist', 'song', 'lyrics', 'features'])

    df[['danceability', 'energy', 'key',
         'loudness', 'mode', 'speechiness',
         'acousticness','instrumentalness', 'liveness',
         'valence', 'tempo']] = pd.DataFrame(df.features.to_list(),index=df.index)

    df = df.drop(columns=['features'])
    df.to_csv(filename, index=False)


def get_lyrics(artist, song):
    song_url = '{}-{}-lyrics'.format(str(artist).strip().replace(' ', '-'),
                                     str(song).strip().replace(' ', '-'))

    request = requests.get('http://genius.com/{}'.format(song_url))

    if request.status_code == 200:

        html_code = BeautifulSoup(request.text, features="html.parser")

        lyrics1 = html_code.find("div", class_="lyrics")
        lyrics2 = html_code.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")
        if lyrics1:
            return lyrics1.get_text()
        elif lyrics2:
            return lyrics2.get_text()
        elif lyrics1 == lyrics2 is None:
            return None


def get_lyrics_mus(artist, artist2, song):
    credentials = json.load(open("authorization.json"))
    musixmatch_key = credentials['musixmatch_key']

    if artist2 is not None:
        artist_details = artist + ' feat ' + artist2
    else:
        artist_details = artist
    mus = Musixmatch(musixmatch_key)
    response = mus.matcher_lyrics_get(q_track=song, q_artist=artist_details)

    if len(response['message']['body']) != 0:
        print(response['message']['body']['lyrics']['lyrics_body'])
        return response['message']['body']['lyrics']['lyrics_body']
    return None


def get_credentials():

    credentials = json.load(open("authorization.json"))
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    genius_key = credentials['genius_key']

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    token = client_credentials_manager.get_access_token()
    sp = spotipy.Spotify(auth=token)
    return sp

def get_public_tracks_details(sp):

    playlist_link = "spotify:playlist:6UeSakyzhiEt4NB3UAd6NQ"

    results = sp.playlist(playlist_link)
    songs = results['tracks']['items']

    track_info = []
    for idx, item in enumerate(songs):
        track = item['track']
        artist = track['artists'][0]['name']
        song = track['name']
        song = song.split('(')[0].strip()
        print(idx, track['artists'][0]['name'], '//', track['artists'][1]['name'], "-", track['name'])

        lyrics = get_lyrics_mus(artist, song)
        if lyrics is not None:
            lyrics = lyrics.replace('\n', ' ')
        track_info.append([track['id'], artist, song, lyrics.strip('\n')])

    print(track_info)
    #add_to_dataset(track_info, 'song_dataset.csv')


def get_user_credentials():
    credentials = json.load(open("authorization.json"))
    client_id = credentials['client_id']
    client_secret = credentials['client_secret']
    token = spotipy.util.prompt_for_user_token("spotify:user:varshanatarajan311298", 'user-top-read', client_id=client_id,
                                               client_secret=client_secret, redirect_uri='http://localhost:8000')
    sp2 = spotipy.Spotify(auth=token)
    sp2.trace = False
    return sp2

def construct_features(features):

    result = []
    for key in features:
        result.append(features[key])
    return result

def get_user_top_tracks(sp2):
    track_info = []
    results = sp2.current_user_top_tracks(limit=100)
    for i, item in enumerate(results['items']):
        song = item['name']
        song = song.split('(')[0].strip()
        artist = item['artists'][0]['name']
        id = item['id']
        if len(item['artists']) > 1:
            artist2 = item['artists'][1]['name']
        else:
            artist2 = None
        print(item)
        print(i, item['name'], '//', item['artists'][0]['name'])

        lyrics = get_lyrics_mus(artist, artist2, song)
        if lyrics is None:
            print('passing ', artist, '-', song)
            continue
        lyrics = lyrics.replace('\n', ' ')
        lyrics = lyrics.replace('******* This Lyrics is NOT for Commercial use *******', '')
        features = sp2.audio_features(id)
        features = construct_features(features[0])
        print(features[:11])
        track_info.append([item['id'], artist, song, lyrics.strip('\n'), features[:11]])
    print(track_info)
    add_to_dataset(track_info, 'user_dataset.csv')


if __name__ == '__main__':
    # sp = get_credentials()
    # get_public_tracks_details(sp)
    sp2 = get_user_credentials()
    get_user_top_tracks(sp2)
