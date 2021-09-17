import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from fastapi import Header
from fastapi.templating import Jinja2Templates
import cv2

app = FastAPI()
cam = cv2.VideoCapture(0)
templates = Jinja2Templates(directory="templates")


@app.get('/')
async def root(request: Request):
  return templates.TemplateResponse("index.html", context={"request": request})

def gen(camera):
    while True:
        ret, frame = camera.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        r, jpg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n')
               


@app.get('/video') # Another endpoint for the index to call to generate the image feed
def video_feed():
    return StreamingResponse(gen(cv2.VideoCapture(0)), media_type="multipart/x-mixed-replace;boundary=frame")

def start():
  """Run app using `poetry run start`"""
  uvicorn.run("web_interface.main:app", host="127.0.0.1", port=8080, reload=True)