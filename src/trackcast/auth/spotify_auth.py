import keyring as kr
import spotipy.util as util

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080/callback"
SCOPE = "user-read-currently-playing"

def has_token():
    return kr.get_password("TrackCast", "SPOTIFY_TOKEN") is not None

def authorize():
    token = util.prompt_for_user_token(
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )
    kr.set_password("TrackCast", "SPOTIFY_TOKEN", token)
