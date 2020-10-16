import json
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

credentials = json.load(open("authorization.json"))
client_id = credentials['client_id']
client_secret = credentials['client_secret']
user_id = credentials['user_id']

token = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

cache_token = token.get_access_token()
sp = spotipy.Spotify(cache_token)


def get_artist(name):
    results = sp.search(q='artist:'+name, type='artist')
    items = results['artists']['items']
    return items[0]


def show_recommendations(artist):
    albums = []
    result = sp.recommendations(seed_artists=[artist['id']])
    for track in result['tracks']:
        print(track['name'], '-', track['artists'][0]['name'])

