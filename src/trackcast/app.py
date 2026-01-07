from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
import importlib.resources as pkg_resources

from trackcast.track_manager import manager
import trackcast.web  # <- пакет web, где лежат index.html, style.css, script.js

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# API текущего трека
# ----------------------
@app.get("/track")
def get_track():
    return manager.get_track() or {}

# ----------------------
# HTML виджет
# ----------------------
@app.get("/widget")
def widget():
    html_bytes = pkg_resources.read_binary(trackcast.web, "index.html")
    html_str = html_bytes.decode("utf-8")
    return HTMLResponse(content=html_str)

# ----------------------
# CSS виджет
# ----------------------
@app.get("/widget/style.css")
def widget_css():
    css_bytes = pkg_resources.read_binary(trackcast.web, "style.css")
    return Response(content=css_bytes, media_type="text/css")

# ----------------------
# JS виджет
# ----------------------
@app.get("/widget/script.js")
def widget_js():
    js_bytes = pkg_resources.read_binary(trackcast.web, "script.js")
    return Response(content=js_bytes, media_type="application/javascript")
