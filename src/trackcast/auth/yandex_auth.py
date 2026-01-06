import keyring as kr

def has_token():
    return kr.get_password("TrackCast", "YANDEX_TOKEN") is not None

def save_token(token: str):
    kr.set_password("TrackCast", "YANDEX_TOKEN", token)
