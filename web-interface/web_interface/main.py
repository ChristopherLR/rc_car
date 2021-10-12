import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from imutils.video import VideoStream
import cv2
import asyncio
from threading import Thread, Lock

app = FastAPI()
global frame
frame = None
vs = VideoStream(src=0).start()
templates = Jinja2Templates(directory="templates")
lock = Lock()

@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

def gen():
    global frame

    while True:

        frame = vs.read()
        r, jpg = cv2.imencode('.jpg', frame)

        if not r:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n')
               

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

@app.get('/video') # Another endpoint for the index to call to generate the image feed
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace;boundary=frame")

def start():
    """Run app using `poetry run start`"""
    uvicorn.run("web_interface.main:app", host="127.0.0.1", port=8080, reload=True)
