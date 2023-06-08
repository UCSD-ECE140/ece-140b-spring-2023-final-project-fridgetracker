from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles       # for serving static files
# for generating HTML from templatized files
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
# import mysql.connector
# from dotenv import load_dotenv
# import os
import bcrypt
import db_utils as db
import requests
import cv2
import time
import secrets

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

enable = 0


# def gen_frames():
#     if enable:
#         cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX)
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Basic get routes

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# load homepage


@app.get("/", response_class=HTMLResponse)
def get_homescreen(request: Request) -> HTMLResponse:
    # with open("views/HomeScreen.html") as html:
    #     return HTMLResponse(content=html.read())
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        items = db.get_category('')
        return views.TemplateResponse("HomeScreen.html", {"request": request, "items": items})
    return RedirectResponse(url='/login.html')


@app.get("/ViewRecipe.html", response_class=HTMLResponse)
def get_viewrecipe(request: Request) -> HTMLResponse:
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        with open("views/ViewRecipe.html") as html:
            return HTMLResponse(content=html.read())
    return RedirectResponse(url='/login.html')


@app.get("/ViewRecipe.html/{section}", response_class=HTMLResponse)
def get_viewrecipe(request: Request, section: str):
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        return views.TemplateResponse("views/ViewRecipe.html", {"request": request, "section": section})
    return RedirectResponse(url='/login.html')

@app.get("/CreateRecipe.html", response_class=HTMLResponse)
def get_createrecipe(request:Request) -> HTMLResponse:
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        with open("views/CreateRecipe.html") as html:
            return HTMLResponse(content=html.read())
    return RedirectResponse(url='/login.html')


@app.get("/cam.html", response_class=HTMLResponse)
def get_camera(request: Request):
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
       return views.TemplateResponse("cam.html", {"request": request})
    return RedirectResponse(url='/login.html')


# @app.get("/test.html", response_class=HTMLResponse)
# def get_camera():
#     with open("views/test.html") as html:
#         return HTMLResponse(content=html.read())


@app.get("/HomeScreen.html", response_class=HTMLResponse)
def home_screen(request: Request):
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        return views.TemplateResponse("/HomeScreen.html", {"request": request})
    return RedirectResponse(url='/login.html')


@app.get("/login.html", response_class=HTMLResponse)
def login_html(request: Request):
    session = request.cookies.get('session_id')
    if (session and db.select_session(session)):
        return RedirectResponse(url='/')
    return views.TemplateResponse("/login.html", {"request": request})

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
    data = []
    if (category == 'All'):
        data = db.get_category()
    else:
        data = db.get_category(category)
    return data


# delete an item given the item name(string) and the section(string)
@app.delete('/delete_item')
def delete_item(item: Item):
    if db.delete_item(item.itemName, item.listTage):
        return {'message': 'Item sucessfully deleted.'}
    return {'message': 'Item not deleted!'}


# update an item given an old item(Item) and new item(Item)
@app.put('/update_item')
def update_item(oldItem:Item, newItem:Item):
    if db.update_item(oldItem.itemName, oldItem.listTage, newItem.itemName, newItem.addedDate, newItem.expiredDate):
        return {'message': 'Item updated successfully.'}
    return {'message': 'Item not updated!'}


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Login/Registration

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: str
    pwd: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.get('/logout', response_class=RedirectResponse)
async def get_home(request:Request, response:Response) -> HTMLResponse:
  session = request.cookies.get('session_id')
  if (session and db.select_session(session)):
    if(db.delete_session(session)):
      response.delete_cookie(key='session_id')
  return RedirectResponse('/login.html')

@app.post('/login')
async def post_login(visitor:UserLogin, response:Response):
  if(db.check_user_password(visitor.email,visitor.password)):
    session_id = secrets.token_hex(16)
    if (db.create_session(session_id, visitor.email)):
      response.set_cookie(key='session_id', value=session_id)
      return {'status': 'success'}
    return {'status': 'error'}
  return {'status': 'wrong credentials'}

@app.post('/register')
def post_registration(user:UserRegistration):
    return {'status': 'success', 'first_name': user.first_name} if db.create_user(user.first_name,user.last_name,user.email,bcrypt.hashpw(user.pwd.encode('utf-8'), bcrypt.gensalt())) else {'status': 'error'}

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Camera and Barcode API

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def gen_frames():
    global productdata, enable
    while True:
        if enable:
            ret, frame = cap.read()
            if ret:
                ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
                if ret_bc:
                    frame = cv2.polylines(frame, points.astype(int), True, (0, 255, 0), 3)
                    
                    for s, p in zip(decoded_info, points):
                        
                        # if a valid barcode value is found
                        if s:                    
                            # shift data through a 5 element list each time a new barcode is detected, with the newest barcode at index 0
                            # and the oldest at index 4. If a new barcode is detected, the list shifts up by one (data @ index 0 -> index 1),
                            # the barcode previously at index 4 is discarded, and the new barcode is added at index 0
                            for i in reversed(range(len(barcodes))):
                                barcodes[i] = barcodes[i-1]
                            barcodes[0] = s

                    # if all elements in the barcodes list are the same (aka the scanner has scanned the same barcode number 5 times in a row)
                    if len(set(barcodes)) == 1:
                        # retrieve product data from api
                        rawdata = requests.get('https://api.barcodelookup.com/v3/products?barcode=%s&key=6zusy8frdfgq2uriti6lu5v74ws6n5' % barcodes[0]).json()
                        productdata = rawdata['products'][0]['title']

                        enable = 0
                        break

                # yield (b'--frame\r\n'
                #     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                _, frame = cv2.imencode('.jpeg', frame)  # Convert frame to a byte string

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')  # Concatenate byte strings


# GET request - basic video feed
@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/enable_scan')
def scan_enabled():
    global productdata, enable 
    enable = 1
    productdata = 0

    while (productdata == 0):
        time.sleep(1)
    
    return {'product': productdata}




# Run the FastAPI application
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='100.80.247.53', port=8000)
    # uvicorn.run(app, host='0.0.0.0', port=8000)












######junkyard

# detection_option = -1
# qr_code = ""

# def gen_frames():
#     global detection_option, qr_code
#     while True:
#         success, frame = cap.read()  # use frame variable for other image processing     
#         frame, qr_code = detect_barcodes(frame) # detect qr code
#         if not success:
#             break
#         else:
#             cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX) # adjust frame brightness
#             ret, buffer = cv2.imencode('.jpg', frame)   # encode image into buffer
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # uvicorn.run(app, host='100.80.240.83', port=8000)
    # uvicorn.run(
    #     app,
    #     host='192.168.0.34',
    #     port=8000,
    #     ssl_keyfile="key.pem",
    #     ssl_certfile="cert.pem",
    # )

    # 100.80.240.83
    # uvicorn.run(app, host='0.0.0.0', port=8000)
    # uvicorn.run(app, host='192.168.1.245', port=8000)
# GET index homepage
# @app.get('/cam.html')
# def index(request: Request):
#     global qr_code
#     return templates.TemplateResponse("cam.html", {"request": request, 'qr_code': qr_code})


# new GET request that takes int detect_opt, shows the detected object video stream
# @app.get('/video_feed/{detect_opt}')
# def video_feed(detect_opt:int = -1):
#     global detection_option
#     detection_option = detect_opt
#     return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# qr code endpoint
# @app.get('/get_qr_code')
# def get_qr_code():
#     global qr_code
#     return qr_code


# detected_barcodes =[]
# def detect_barcodes(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     barcodes = pyzbar.decode(gray)

#     global detected_barcodes 
#     for barcode in barcodes:
#         barcode_data = barcode.data.decode("utf-8")
#         barcode_type = barcode.type

#         # Extract the bounding box coordinates of the barcode
#         (x, y, w, h) = barcode.rect

#         # Add the barcode information to the list
#         detected_barcodes.append({
#             "data": barcode_data,
#             "type": barcode_type,
#             "bounding_box": (x, y, w, h)
#         })

#         # Draw the bounding box around the barcode on the frame
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         # Put the barcode data and type as text on the frame
#         text = f"{barcode_data} ({barcode_type})"
#         cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#     cv_barcode_get()
#     return frame, detected_barcodes

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

# @app.get('/getbarcode')
# async def cv_barcode_get():
#     global cap, detected_barcodes
#     barcodes = detect_barcodes
#     # enable = True

#     # while enable:
#     #     ret, frame = cap.read()
#     #     if ret:
#     #         ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
#     #         if ret_bc:
#     #             for s, p in zip(decoded_info, points):
#     #                 if s:
#     #                     barcodes = [s] + barcodes[:-1]

#     if len(set(barcodes)) == 1:
#         print(barcodes)
#         rawdata = requests.get(
#             'https://api.barcodelookup.com/v3/products?barcode=%s&key=YOUR_API_KEY' % barcodes[0]).json()
#         productdata = rawdata['products'][0]

#         enable = False

#         return productdata['title']

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