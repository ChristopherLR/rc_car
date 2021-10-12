import uvicorn
from fastapi import FastAPI
from fastapi import Request, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import aioredis
import asyncio
import async_timeout


app = FastAPI()
templates = Jinja2Templates(directory="templates")
redis = aioredis.from_url("redis://localhost")
pubsub = redis.pubsub()

@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request, "feed": f'video' })

async def gen():
    while True:
        img = await redis.get('video')
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
               
@app.get('/video') # Another endpoint for the index to call to generate the image feed
def video_feed():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace;boundary=frame")

@app.websocket("/buttons")
async def button_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await pubsub.subscribe('channel:1')
    message = None
    while True:
        try:
            async with async_timeout.timeout(0.1):
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    data = message['data'].decode('UTF-8')
                    await websocket.send_text(f'count is: {data}')
                await asyncio.sleep(0.001)
        except asyncio.TimeoutError:
            continue

def start():
    uvicorn.run("web_interface.main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == '__main__':
    start()