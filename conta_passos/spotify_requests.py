from secrets_client import client_id,client_secret
import os
from spotify_client import SpotifyClient
import requests
from base64 import b64encode
import json
#authentication

def get_auth_token():
    url = 'https://accounts.spotify.com/api/token'

    # Set the request parameters
    payload = {'grant_type': 'client_credentials'}
    headers = {'Authorization': f'Basic {b64encode((client_id + ":" + client_secret).encode()).decode()}'}

    # Make the POST request
    response = requests.post(url, data=payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Print the access token
        return response.json()['access_token']
    else:
        # Print the error message
        print(response.json()['error'])


def play_song(song_string):
    auth_token = get_auth_token()
    client = SpotifyClient(auth_token)
    playlist_url = client.get_playlist_url(song_string)
    track_id = client.get_track_id_from_playlist(playlist_url)
    return "spotify:track:"+track_id
    

    