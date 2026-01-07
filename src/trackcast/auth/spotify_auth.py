import os
import time
import keyring as kr
from spotipy.oauth2 import SpotifyOAuth

SERVICE = "TrackCast"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8080/callback"
SCOPE = "user-read-currently-playing"

def has_token():
    return kr.get_password(SERVICE, "SPOTIFY_REFRESH_TOKEN") is not None

def authorize():
    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        open_browser=True
    )

    token_info = oauth.get_access_token(as_dict=True)

    kr.set_password(SERVICE, "SPOTIFY_ACCESS_TOKEN", token_info["access_token"])
    kr.set_password(SERVICE, "SPOTIFY_REFRESH_TOKEN", token_info["refresh_token"])
    kr.set_password(SERVICE, "SPOTIFY_EXPIRES_AT", str(token_info["expires_at"]))

def get_valid_token():
    refresh = kr.get_password(SERVICE, "SPOTIFY_REFRESH_TOKEN")
    expires_at = kr.get_password(SERVICE, "SPOTIFY_EXPIRES_AT")
    access = kr.get_password(SERVICE, "SPOTIFY_ACCESS_TOKEN")

    if not refresh or not expires_at:
        return None

    expires_at = int(expires_at)

    oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    if time.time() > expires_at - 60:
        token_info = oauth.refresh_access_token(refresh)

        kr.set_password(SERVICE, "SPOTIFY_ACCESS_TOKEN", token_info["access_token"])
        kr.set_password(SERVICE, "SPOTIFY_EXPIRES_AT", str(token_info["expires_at"]))

        return token_info["access_token"]

    return access

