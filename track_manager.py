import threading
import time

from services.spotify import get_now_playing as spotify_now
from services.yandex import get_now_playing as yandex_now


class TrackManager:
    def __init__(self):
        self.active_service = None   # "spotify" | "yandex" | None
        self.track_data = None
        self.running = False

        self._thread = None
        self._lock = threading.Lock()

    def start(self, service: str):
        if service not in ("spotify", "yandex"):
            raise ValueError("Unknown service")

        # гарантируем, что запущен только один сервис
        self.stop()

        self.active_service = service
        self.running = True
        self._thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self.running = False
        self.active_service = None

    def _loop(self):
        while self.running:
            try:
                if self.active_service == "spotify":
                    data = spotify_now()
                elif self.active_service == "yandex":
                    data = yandex_now()
                else:
                    data = None

                with self._lock:
                    self.track_data = data

            except Exception as e:
                print("[TrackManager]", e)

            time.sleep(1)

    def get_track(self):
        with self._lock:
            return self.track_data


# singleton
manager = TrackManager()
