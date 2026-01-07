import sys
import threading
import os
import getpass
from pathlib import Path

import uvicorn
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QInputDialog,
    QSystemTrayIcon,
    QMenu,
    QLabel
)
from PySide6.QtGui import QIcon, QCursor
from PySide6.QtCore import Qt

from trackcast.track_manager import manager
from trackcast.app import app

from trackcast.auth.spotify_auth import (
    has_token as spotify_has_token,
    authorize as spotify_authorize
)
from trackcast.auth.yandex_auth import (
    has_token as yandex_has_token,
    save_token as yandex_save_token
)


# ======================
# FastAPI runner
# ======================
def run_api():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="warning"
    )


# ======================
# Main window
# ======================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TrackCast")
        self.setFixedSize(400, 250)

        # Кнопки
        self.btn_yandex = QPushButton()
        self.btn_spotify = QPushButton()
        self.btn_reset_tokens = QPushButton("Сбросить токены")  # новая кнопка

        # OBS label
        self.obs_label = QLabel()
        self.obs_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.obs_label.setOpenExternalLinks(False)
        self.obs_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.obs_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.obs_label.hide()
        self.obs_label.mousePressEvent = self.copy_obs_link

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_yandex)
        layout.addWidget(self.btn_spotify)
        layout.addWidget(self.btn_reset_tokens)
        layout.addWidget(self.obs_label)

        # Handlers
        self.btn_yandex.clicked.connect(self.handle_yandex)
        self.btn_spotify.clicked.connect(self.handle_spotify)
        self.btn_reset_tokens.clicked.connect(self.reset_tokens)

        self.update_buttons()

    # ---------- UI state ----------
    def update_buttons(self):
        # Yandex
        if not yandex_has_token():
            self.btn_yandex.setText("Подключить Yandex Music")
        else:
            self.btn_yandex.setText(
                "Остановить Yandex Music"
                if manager.active_service == "yandex"
                else "Запустить Yandex Music"
            )

        # Spotify
        if not spotify_has_token():
            self.btn_spotify.setText("Подключить Spotify")
        else:
            self.btn_spotify.setText(
                "Остановить Spotify"
                if manager.active_service == "spotify"
                else "Запустить Spotify"
            )

        # OBS label
        if manager.active_service:
            self.obs_label.setText(f"Ссылка для OBS: http://127.0.0.1:8000/widget")
            self.obs_label.show()
        else:
            self.obs_label.hide()

    # ---------- Handlers ----------
    def handle_yandex(self):
        if not yandex_has_token():
            self.connect_yandex()
            return

        if manager.active_service == "yandex":
            manager.stop()
        else:
            manager.start("yandex")

        self.update_buttons()

    def handle_spotify(self):
        if not spotify_has_token():
            spotify_authorize()
            self.update_buttons()
            return

        if manager.active_service == "spotify":
            manager.stop()
        else:
            manager.start("spotify")

        self.update_buttons()

    # ---------- Auth ----------
    def connect_yandex(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Yandex Music")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(
            "Установите расширение для браузера:<br>"
            "Chrome: <a href='https://chrome.google.com/webstore/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib'>ссылка</a><br>"
            "Firefox: <a href='https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/'>ссылка</a><br><br>"
            "После установки зайдите на <a href='https://music.yandex.ru'>music.yandex.ru</a>, "
            "откройте расширение и нажмите «Скопировать токен»<br>"
            "И введите его в следующем окне"
        )
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        token, ok = QInputDialog.getText(
            self,
            "Yandex Token",
            "Введите токен:"
        )

        if ok and token:
            yandex_save_token(token)
            self.update_buttons()

    # ---------- OBS label click ----------
    def copy_obs_link(self, event):
        if manager.active_service:
            clipboard = QApplication.clipboard()
            clipboard.setText("http://127.0.0.1:8000/widget")
            msg = QMessageBox(self)
            msg.setWindowTitle("Скопировано")
            msg.setText("Ссылка для OBS скопирована в буфер!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    # ---------- Reset tokens ----------
    def reset_tokens(self):
        reply = QMessageBox.question(
            self,
            "Сброс токенов",
            "Вы уверены, что хотите удалить токены Spotify и Yandex? Это потребует повторной авторизации.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        import keyring as kr

        # --- Yandex ---
        try:
            kr.delete_password("TrackCast", "YANDEX_TOKEN")
        except Exception as e:
            print(f"[ResetTokens] Failed to remove Yandex token: {e}")

        # --- Spotify ---
        try:
            kr.delete_password("TrackCast", "SPOTIFY_TOKEN")
        except Exception as e:
            print(f"[ResetTokens] Failed to remove Spotify token: {e}")

        # Удаляем .cache-USERNAME (Spotipy)
        try:
            username = getpass.getuser()
            cache_file = Path(f".cache-{username}")
            if cache_file.exists():
                cache_file.unlink()
        except Exception as e:
            print(f"[ResetTokens] Failed to remove Spotipy cache: {e}")

        QMessageBox.information(
            self,
            "Сброс токенов",
            "Токены успешно удалены. Вам нужно будет снова авторизоваться."
        )

        self.update_buttons()

    # ---------- Tray behaviour ----------
    def closeEvent(self, event):
        event.ignore()
        self.hide()


# ======================
# Entry point
# ======================
def main():
    threading.Thread(target=run_api, daemon=True).start()

    qt_app = QApplication(sys.argv)
    window = MainWindow()

    tray = QSystemTrayIcon(QIcon("icon.png"), qt_app)
    tray_menu = QMenu()

    tray_menu.addAction("Открыть", window.show)
    tray_menu.addSeparator()
    tray_menu.addAction("Выход", qt_app.quit)

    tray.setContextMenu(tray_menu)
    tray.show()

    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
