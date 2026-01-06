import spotipy
import keyring as kr

def get_now_playing():
    token = kr.get_password("TrackCast", "SPOTIFY_TOKEN")
    if not token:
        return None

    spotify = spotipy.Spotify(auth=token)
    current = spotify.current_user_playing_track()
    if not current or not current.get("is_playing"):
        return None

    item = current.get("item")
    if not item:
        return None

    return {
        "service": "spotify",
        "title": item["name"],
        "artists": [a["name"] for a in item["artists"]],
        "cover": item["album"]["images"][0]["url"],
        "duration": item["duration_ms"] // 1000
    }
