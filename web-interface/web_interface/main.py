import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from imutils.video import VideoStream
import cv2
<<<<<<< HEAD
from websockets import serve
import asyncio
from threading import Thread


app = FastAPI()
templates = Jinja2Templates(directory="templates")
CLIENTS = set()

@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "test": 'key'})

global camera
camera = cv2.VideoCapture(0)

async def video_stream():
    print("Running Video Stream")
    while True:
        ret, frame = camera.read()
=======
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
>>>>>>> fdf3e9f (reverted to simple streaming response)

    while True:

        frame = vs.read()
        r, jpg = cv2.imencode('.jpg', frame)
<<<<<<< HEAD
        bytes_jpg = jpg.tobytes()
        
        for ws in CLIENTS:
            await ws.send(bytes_jpg)

async def handler(websocket, path):
    CLIENTS.add(websocket)
    try:
        async for msg in websocket:
            pass
    finally:
        CLIENTS.remove(websocket)

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()
=======

        if not r:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n')
               
>>>>>>> fdf3e9f (reverted to simple streaming response)

def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

<<<<<<< HEAD
async def socket_server() -> None:
    async with serve(handler, '0.0.0.0', 8765):
        await asyncio.Future()


def start():
    loop1 = asyncio.new_event_loop()
    loop2 = asyncio.new_event_loop()
    t1 = Thread(target=start_background_loop, args=(loop1,), daemon=True)
    t2 = Thread(target=start_background_loop, args=(loop2,), daemon=True)
    t1.start()
    t2.start()

    asyncio.run_coroutine_threadsafe(socket_server(), loop1)
    asyncio.run_coroutine_threadsafe(video_stream(), loop2)

    uvicorn.run("web_interface.main:app", host="0.0.0.0", port=8080, reload=True),
    loop1.stop()
    loop2.stop()

if __name__ == '__main__':
    start()
=======
@app.get('/video') # Another endpoint for the index to call to generate the image feed
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace;boundary=frame")

def start():
    """Run app using `poetry run start`"""
    uvicorn.run("web_interface.main:app", host="127.0.0.1", port=8080, reload=True)
>>>>>>> fdf3e9f (reverted to simple streaming response)
