from yandex_music import Client
import keyring as kr
import requests

def get_now_playing():
    token = kr.get_password("TrackCast", "YANDEX_TOKEN")
    if not token:
        return None

    r = requests.get(
        "http://track.mipoh.ru/get_current_track_beta",
        headers={"ya-token": token},
        timeout=3
    ).json()

    track_id = r["track"]["track_id"]
    client = Client(token).init()
    track = client.tracks(track_id)[0]

    return {
        "service": "yandex",
        "title": track.title,
        "artists": [a.name for a in track.artists],
        "cover": f"https://{track.cover_uri.replace('%%', '400x400')}"
    }
