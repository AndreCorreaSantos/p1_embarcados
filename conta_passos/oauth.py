from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from secrets_client import *
import requests
import uvicorn
from spotify_requests import *




# client_id = "YOUR_CLIENT_ID"
# client_secret = "YOUR_CLIENT_SECRET"
# redirect_uri = "YOUR_REDIRECT_URI" # e.g. http://localhost:8000/callback/ --> you will have to whitelist this url in the spotify developer dashboard 



app = FastAPI()

def get_access_token(auth_code: str):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
        },
        auth=(client_id, client_secret),
    )
    access_token = response.json()["access_token"]
    return {"Authorization": "Bearer " + access_token}


@app.get("/")
async def auth():
    scope = ["playlist-modify-private", "playlist-modify-public","user-modify-playback-state"]
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={' '.join(scope)}"
    return HTMLResponse(content=f'<a href="{auth_url}">Authorize</a>')

headers = ''
data_list = []

@app.get("/callback")
async def callback(code):
    global headers
    headers = get_access_token(code)
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_id = response.json()["id"]

    name = "Name of your playlist"
    description = "Description of your playlist"

    params = {
        "name": name,
        "description": description,
        "public": True,
    }

    track_uri = play_song("clowncore flat earth")
    response = requests.put(
        f"https://api.spotify.com/v1/me/player/play",
        headers=headers,
        json={"uris": [track_uri]},
    )

    with open("main.html", "r") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)

@app.get("/main")
async def main(request: Request): #preciso mandar os dados da outra thread via request para esse endpoint mas somente mudar de musica quando usuario clicar em nova musica
    # bpm = last_data
    # track_uri = play_song("tecno {} bpm".format(bpm))
    #perform fft in data_list
    data_str = "tecno {0} bpm".format(data)
    track_uri = play_song(data_str)
    response = requests.put(
        f"https://api.spotify.com/v1/me/player/play",
        headers=headers,
        json={"uris": [track_uri]},
    )


    with open("main.html", "r") as f:
        html_content = f.read()


    html_content = html_content.format(data)
    return HTMLResponse(content=html_content)

max_val = 50
data = 0
@app.put("/main")
async def dataMain(request: Request):
    global data
    
    data = await request.json()
    data = data['data']



uvicorn.run(app)