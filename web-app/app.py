from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles       # for serving static files
# for generating HTML from templatized files
from fastapi.templating import Jinja2Templates
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


@app.get("/cam.html", response_class=HTMLResponse)
def get_camera() -> HTMLResponse:
    with open("views/cam.html") as html:
        return HTMLResponse(content=html.read())
    
@app.get("/test.html", response_class=HTMLResponse)
def get_camera() -> HTMLResponse:
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

@app.get('/getbarcode')
async def cv_barcode_get():
    global frame, enable

    enable = 1

    while True:
        ret, frame = cap.read()
        if ret:
            ret_bc, decoded_info, _, points = bd.detectAndDecode(frame)
            if ret_bc:
                
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
                    productdata = rawdata['products'][0]
                    
                    enable = 0

                    return productdata['title']
                

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

    #uvicorn.run(app, host='192.168.0.34', port=8000)
    # uvicorn.run(app, host='100.80.240.83', port=8000)
    uvicorn.run(
        app,
        host='192.168.0.34',
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )

    # 100.80.240.83
    #uvicorn.run(app, host='0.0.0.0', port=8000)
