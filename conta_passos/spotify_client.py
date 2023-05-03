import random
import string
import urllib
import requests

class SpotifyClient(object):
    def __init__(self,api_key):
        self.api_key = api_key
    
    def get_playlist_url(self,query):
        
        limit = 5
        url = f'https://api.spotify.com/v1/search?q={query}&type=playlist&limit={limit}'
        response = requests.get(
            url,
            headers={
            "Content-Type":'application/json',
            "Authorization":f"Bearer {self.api_key}"
            }
        )
        playlist_url = response.json()['playlists']['items'][0]['tracks']['href']

        return playlist_url

    def get_track_id_from_playlist(self,url):
        
        limit = 5
        response = requests.get(
            url,
            headers={
            "Content-Type":'application/json',
            "Authorization":f"Bearer {self.api_key}"
            }
        )
        tracks = response.json()
        
        rand_n = random.randint(0,len(tracks['items'])-1)

        return tracks['items'][rand_n]['track']['id'] #getting the id from the first track of the playlist

    def play_track(self,track_id):

        headers={
            "Content-Type":'application/json',
            "Authorization":f"Bearer {self.api_key}"
            }

        # Set request body
        data = {
            "uri": f"spotify:track:{track_id}"
        }

        # Make POST request to add track to queue
        response = requests.put("https://api.spotify.com/v1/me/player/queue", headers=headers, json=data)

        return response

    def pause_track(self):

        response = requests.put("https://api.spotify.com/v1/me/player/pause", headers={"Authorization": f"Bearer {self.api_key}"})
        return response.content

    
    def add_tracks_to_library(self,track_id):
        url = 'https://api.spotify.com/v11/me/tracks'
        response = requests.put(
            url,
            headers={
            "Content-Type":'application/json',
            "Authorization":f"Bearer {self.api_key}"
            },
            json={
            'ids': track_id
            }
        )

        return response