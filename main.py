from fastapi import FastAPI, Request, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime
import re

MM_API_URL = 'https://api.mymemory.translated.net/get?q={}&langpair={}'

app = FastAPI(title='List API')
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


def get_translation(input: str) -> str:
    if not input.isalpha():
        return 'Введите русские или английские слова'

    if has_cyrillic(input):
        langs = 'ru|en'
    else:
        langs = 'en|ru'
    try:
        mm_response = requests.get(MM_API_URL.format(input, langs)).json()
    except requests.exceptions.RequestException:
        return 'Извините, ошибка сервера'
    except Exception:
        return 'Что-то пошло не так'

    return mm_response['responseData']['translatedText']


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        recv_data = await websocket.receive_json()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M")

        send_data = {
            'agent':recv_data['agent'],
            'timestamp': dt_string,
            'input': recv_data['text'],
            'output': get_translation(recv_data['text'])
        }
        await websocket.send_json(send_data)
