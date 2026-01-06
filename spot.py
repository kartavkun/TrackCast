# spotify.py
import spotipy
import keyring as kr

token = kr.get_password("TrackCast", "SPOTIFY_TOKEN")

spotify = spotipy.Spotify(auth=token)
# current_track = spotify.current_user_playing_track()
#
# print(current_track)
current_track = spotify.current_user_playing_track()
item = current_track.get('item')

if item is not None and current_track.get('is_playing') is True:
    # Название трека
    title = item.get('name')

    # Артисты
    artists = [artist['name'] for artist in item.get('artists', [])]

    # Обложка — берём самую крупную картинку
    album_images = item.get('album', {}).get('images', [])
    cover_url = album_images[0]['url'] if album_images else None

    # Длительность в секундах
    duration_ms = item.get('duration_ms', 0)
    duration_sec = duration_ms // 1000
    print(f"Сейчас играет: {title}")
    print(f"Артисты: {artists}")
    print(f"Длительность: {duration_sec} секунд")
    print(f"Обложка: {cover_url}")
else:
    print("Сейчас ничего не играет")
