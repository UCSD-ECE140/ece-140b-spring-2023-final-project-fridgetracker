from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles       # for serving static files
# for generating HTML from templatized files
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt
import db_utils as db
import requests
import cv2

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Configuration

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# Create a FastAPI application
app = FastAPI()

# mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
# specify where the HTML files are located
views = Jinja2Templates(directory='views')
templates = Jinja2Templates(directory="templates")
# Define a Pydantic model for the item data


class Item(BaseModel):
    listTage: str
    itemName: str
    addedDate: str
    expiredDate: str


camera_id = 0   # default value is 0 if you only have one camera
delay = 1

bd = cv2.barcode.BarcodeDetector()
cap = cv2.VideoCapture(camera_id)

barcodes = [0]*5

frame = 0
enable = 0


def gen_frames():
    if enable:
        cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Basic get routes

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# load homepage


@app.get("/", response_class=HTMLResponse)
def get_homescreen(request: Request) -> HTMLResponse:
    # with open("views/HomeScreen.html") as html:
    #     return HTMLResponse(content=html.read())
    items = db.get_category('')
    return views.TemplateResponse("HomeScreen.html", {"request": request, "items": items})


@app.get("/ViewRecipe.html", response_class=HTMLResponse)
def get_viewrecipe() -> HTMLResponse:
    with open("views/ViewRecipe.html") as html:
        return HTMLResponse(content=html.read())


@app.get("/ViewRecipe.html/{section}", response_class=HTMLResponse)
def get_viewrecipe(request: Request, section: str):
    return views.TemplateResponse("views/ViewRecipe.html", {"request": request, "section": section})


@app.get("/CreateRecipe.html", response_class=HTMLResponse)
def get_createrecipe() -> HTMLResponse:
    with open("views/CreateRecipe.html") as html:
        return HTMLResponse(content=html.read())


# @app.get("/cam.html", response_class=HTMLResponse)
# def get_camera(request: Request):
#     return views.TemplateResponse("cam.html", {"request": request})


@app.get("/test.html", response_class=HTMLResponse)
def get_camera():
    with open("views/test.html") as html:
        return HTMLResponse(content=html.read())

# Render the HomeScreen.html template


@app.get("/HomeScreen.html", response_class=HTMLResponse)
def home_screen(request: Request):
    return views.TemplateResponse("/HomeScreen.html", {"request": request})


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Kitchen action routes

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# add an item (requests an item to be sent)


@app.post('/add_item')
def add_item(item: Item) -> dict:
    if db.add_item(item.listTage, item.itemName, item.addedDate, item.expiredDate):
        return {'message': 'Item added successfully'}
    return {'message': 'Item not added!'}


# retrieve FridgeListS/CounterItemS/PantryItemS/ShoppingListS items list
@app.get('/get_{category}_list')
def get_category_list(category: str) -> list:
    data = db.get_category(category)
    if data:
        return data
    else:
        return []


@app.delete('/delete_item')
def delete_item(item: Item):
    if db.delete_item(item.listTage):
        return {'message': 'Item deleted.'}
    return {'message': 'Item not deleted!'}


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Login/Registration

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# Login/Registration


class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: str
    user: str
    pwd: str
    kitchen_id: int
    user_role: int


@app.post('/register_user')
def register_user(user: UserRegistration):
    # Encrypt password here on the server
    pwd = bcrypt.hashpw(user.pwd.encode('utf-8'), bcrypt.gensalt())
    if db.create_user(user.first_name, user.last_name, user.email, user.user, pwd, user.kitchen_id, user.user_role):
        return {'message': 'User registered.'}
    return {'message': 'User not registered!'}


# TODO: Login user
class UserLogin(BaseModel):
    username: str
    password: str


@app.post('/login_user')
def login_user(user: UserLogin):
    # Retrieve user data from the database using user.username
    user_data = db.get_user(user.username)
    if user_data:
        hashed_password = user_data['password']
        if bcrypt.checkpw(user.password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Redirect to HomeScreen.html
            return RedirectResponse(url='views/HomeScreen.html')
    raise HTTPException(status_code=401, detail='Invalid username or password')


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Camera and Barcode API

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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


detected_barcodes =[]
def detect_barcodes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)

    global detected_barcodes 
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
    cv_barcode_get()
    return frame, detected_barcodes

# @app.get('/video_feed')
# async def video_feed():
#     global cap

#     async def gen_frames():
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 ret, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#     return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/getbarcode')
async def cv_barcode_get():
    global cap, detected_barcodes
    barcodes = detect_barcodes
    # enable = True

    # while enable:
    #     ret, frame = cap.read()
    #     if ret:
    #         ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
    #         if ret_bc:
    #             for s, p in zip(decoded_info, points):
    #                 if s:
    #                     barcodes = [s] + barcodes[:-1]

    if len(set(barcodes)) == 1:
        print(barcodes)
        rawdata = requests.get(
            'https://api.barcodelookup.com/v3/products?barcode=%s&key=YOUR_API_KEY' % barcodes[0]).json()
        productdata = rawdata['products'][0]

        enable = False

        return productdata['title']

# @app.get('/video_feed')
# def video_feed():
#     return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


# @app.post("/barcode")
# def retrieve_barcode_info(barcodes):
#     # print(barcodes)
#     print("hello")

# @app.post('/barcode')
# async def process_barcode(data: dict):
#     barcode = data.get('barcode')
#     # Do something with the barcode string
#     # You can add your processing logic here
#     print(barcode)
#     print(type(barcode))
#     rawdata = requests.get(
#         'https://api.barcodelookup.com/v3/products?barcode=%s&key=27lavzpbu9png7o8dpuekaiosxq1d6' % barcode)
#     print(rawdata)
#     jsondata = rawdata.json()
#     print(jsondata)
#     productdata = jsondata['products'][0]['title']
#     print(productdata)
#     return {'product': productdata}

    # Return a response
    # return {'message': 'Barcode processed successfully'}


# Run the FastAPI application
if __name__ == '__main__':
    import uvicorn

    # uvicorn.run(app, host='192.168.0.38', port=8000)
    # uvicorn.run(app, host='100.80.240.83', port=8000)
    # uvicorn.run(
    #     app,
    #     host='192.168.0.34',
    #     port=8000,
    #     ssl_keyfile="key.pem",
    #     ssl_certfile="cert.pem",
    # )

    # 100.80.240.83
    uvicorn.run(app, host='0.0.0.0', port=8000)
