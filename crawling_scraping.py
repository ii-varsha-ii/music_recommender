import glob
from bs4 import BeautifulSoup
import os, errno
from os.path import expanduser
import time
import requests
import json

url = 'https://www.azlyrics.com/'

def get_all_artists(alphabetical_links):
    all_artist_links = []  # Link of all artists for each alphabet
    for link in alphabetical_links[:2]:
        time.sleep(1)
        req = requests.get(link)
        soup = BeautifulSoup(req.text, 'html.parser')

        paging = soup.find_all("div", {'class': "col-sm-6 text-center artist-col"})
        for page in paging:
            all_artist_links += ['/'.join(link.split('/')[:-1]) + '/' + a['href'] for a in
                                 page.find_all('a', href=True)]

    return all_artist_links


def get_all_song_links(all_artist_links):
    all_link_az = []
    for artist in all_artist_links[:2]:  # Link for each song for each artist
        time.sleep(1)
        url = artist
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        paging = soup.find_all("div", {'class': "listalbum-item"})
        for page in paging:
            all_link_az += ['/'.join(artist.split('/')[:-2]) + '/' + '/'.join(a['href'].split('/')[1:]) for a in
                            page.find_all('a', href=True)]
    return all_link_az


def get_all_songs(all_link_az):
    webpage_htmls = {}
    for link in all_link_az[:20]:
        time.sleep(1)
        url = link
        req = requests.get(url)
        webpage_htmls[url] = BeautifulSoup(req.text, 'html.parser')  # html webpage for each song

    return webpage_htmls


def save_to_file(webpage_htmls):
    for key, value in webpage_htmls.items():
        with open('lyrics_collection/' + '_'.join(key.rsplit("/", 2)[-2:]), 'w+') as f1:
            f1.write(str(value.prettify()))


def save_data_to_file(data, link):
    with open(link, 'w+') as f1:
        f1.write(str(data))


def crawling():
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    paging = soup.find_all("div", {'class': 'btn-group text-center'})

    alphabetical_links = ['https:' + a['href'] for a in
                          paging[0].find_all('a', href=True)]  # Link of each alphabet at the top header

    all_artist_links = get_all_artists(alphabetical_links)
    all_link_az = get_all_song_links(all_artist_links)
    webpage_htmls = get_all_songs(all_link_az)
    print(webpage_htmls)
    #save_to_file(webpage_htmls)
    save_data_to_file(webpage_htmls, 'webpages.txt')
    return webpage_htmls

def HTMLtoJSON(path,az):
    #Generate one file JSON given the path of the file and the dictionary (az)
    path = path.split('\\')
    path.insert(1, 'json_folder')
    final_path = '//'.join(path)
    final_path = final_path.replace('.html','.json')
    with open(final_path, 'w+') as file:
        json.dump(az, file)


def scrapping():

    db_table = []
    for filepath in glob.glob(os.path.join('lyrics_collection/', "*.html")):
        with open(filepath, "r", encoding='utf-8', errors='ignore') as f:
            content = f
            print(filepath)
            az = {}
            soup = BeautifulSoup(content, "html.parser")
            artists = soup.find_all('title')
            t = artists[0].text
            t = t.replace('| AZLyrics.com', '')
            t = t.split('-')
            print(t)
            az['artist'] = t[0]
            az['title'] = t[1]

            for br in soup.findAll('br'):
                br.extract()
            lyrics = soup.find("div", {'class': "col-xs-12 col-lg-8 text-center"})
            if lyrics:
                az['lyrics'] = lyrics.get_text(separator=' ')
                az['lyrics'] = az['lyrics'].replace('\n', ' ')
                az['lyrics'] = az['lyrics'].replace('\r', ' ')
            else:
                continue

            az['url'] = filepath
            HTMLtoJSON(filepath, az)
            db_table.append(az)
    return db_table


if __name__ == '__main__':
    #webpages = crawling()

    final_data = scrapping()

    save_data_to_file(final_data, 'final_data.txt')
