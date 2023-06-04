from pyzbar import pyzbar

import cv2
import uvicorn
import numpy as np
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pyzbar import pyzbar
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# global variable to keep track of video streams' detection method
detection_option = -1
qr_code = ""

def gen_frames():
    global detection_option, qr_code
    while True:
        success, frame = cap.read()  # use frame variable for other image processing     
        frame, qr_code = detect_barcodes(frame) # detect qr code
        if not success:
            break
        else:
            cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX) # adjust frame brightness
            ret, buffer = cv2.imencode('.jpg', frame)   # encode image into buffer
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# GET index homepage
@app.get('/cam.html')
def index(request: Request):
    global qr_code
    return templates.TemplateResponse("cam.html", {"request": request, 'qr_code': qr_code})

# GET request - basic video feed
@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# new GET request that takes int detect_opt, shows the detected object video stream
@app.get('/video_feed/{detect_opt}')
def video_feed(detect_opt:int = -1):
    global detection_option
    detection_option = detect_opt
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# qr code endpoint
@app.get('/get_qr_code')
def get_qr_code():
    global qr_code
    return qr_code



def detect_barcodes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)

    detected_barcodes = []
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        # Extract the bounding box coordinates of the barcode
        (x, y, w, h) = barcode.rect

        # Add the barcode information to the list
        detected_barcodes.append({
            "data": barcode_data,
            "type": barcode_type,
            "bounding_box": (x, y, w, h)
        })

        # Draw the bounding box around the barcode on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Put the barcode data and type as text on the frame
        text = f"{barcode_data} ({barcode_type})"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame, detected_barcodes
