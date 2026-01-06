import sys
import threading

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

from track_manager import manager
from app import app

from auth.spotify_auth import (
    has_token as spotify_has_token,
    authorize as spotify_authorize
)
from auth.yandex_auth import (
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
        self.setFixedSize(400, 200)

        self.btn_yandex = QPushButton()
        self.btn_spotify = QPushButton()

        self.obs_label = QLabel()  # для ссылки OBS
        self.obs_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.obs_label.setOpenExternalLinks(False)  # ловим клик сами
        self.obs_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.obs_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.obs_label.hide()
        self.obs_label.mousePressEvent = self.copy_obs_link

        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_yandex)
        layout.addWidget(self.btn_spotify)
        layout.addWidget(self.obs_label)

        self.btn_yandex.clicked.connect(self.handle_yandex)
        self.btn_spotify.clicked.connect(self.handle_spotify)

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

        # Кликабельные ссылки через HTML
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
            # Всплывающее уведомление
            msg = QMessageBox(self)
            msg.setWindowTitle("Скопировано")
            msg.setText("Ссылка для OBS скопирована в буфер!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    # ---------- Tray behaviour ----------
    def closeEvent(self, event):
        # закрытие окна ≠ выход из приложения
        event.ignore()
        self.hide()


# ======================
# Entry point
# ======================

def main():
    # FastAPI в фоне
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
