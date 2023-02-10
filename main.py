import requests
from bs4 import BeautifulSoup
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

URL = "https://www.billboard.com/charts/hot-100/"

date = input("Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ")

# Scraping Billboard 100
response = requests.get(f"{URL}{date}")
page = response.text
soup = BeautifulSoup(page, "html.parser")
songs_name = soup.select(selector="li h3", class_="c-title")
songs_list = [song.get_text().strip() for song in songs_name]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# Searching Spotify for songs by title
song_uris = []
year = date.split("-")[0]
for song in songs_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print("Done.")
