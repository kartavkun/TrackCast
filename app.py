from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from track_manager import manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/track")
def get_track():
    return manager.get_track() or {}

# новый роут для HTML виджета
@app.get("/widget")
def widget():
    widget_path = Path(__file__).parent / "web" / "widget.html"
    return FileResponse(widget_path, media_type="text/html")
