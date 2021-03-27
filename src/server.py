from apps.spotify import SpotifyManager
from apps.code import error_code

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import pprint

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
manager = SpotifyManager()
templates = Jinja2Templates("templates")


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("search.html", context={"request": request})


@app.post('/search')
async def search(request: Request, trackid: str = Form(...), num: int = Form(...)):
    playlist_url, c = manager.searchNearest(trackid, num)
    print(playlist_url, c)

    if playlist_url is None:
        return templates.TemplateResponse("search.html", context={"request": request, "code": error_code[c]})
    else:
        return RedirectResponse(playlist_url + '/')