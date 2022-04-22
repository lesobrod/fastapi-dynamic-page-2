import json
import asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

MM_API_URL = 'https://api.mymemory.translated.net/get?q={}&langpair=ru|en'

app = FastAPI(title='List API')
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_translation(input: str) -> str:
    ...


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        mm_response = requests.get(MM_API_URL.format(data)).json()
        await websocket.send_text(data + ' : ' + mm_response['responseData']['translatedText'])
