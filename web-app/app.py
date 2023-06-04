from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles       # for serving static files
from fastapi.templating import Jinja2Templates    # for generating HTML from templatized files
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt
import db_utils as db

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Configuration

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# Create a FastAPI application
app = FastAPI()

# mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
views = Jinja2Templates(directory='views')        # specify where the HTML files are located

# Define a Pydantic model for the item data
class Item(BaseModel):
    listTage: str
    itemName: str
    addedDate: str
    expiredDate: str

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Basic get routes

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# load homepage
@app.get("/", response_class=HTMLResponse)
def get_homescreen(request:Request) -> HTMLResponse:
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


# Render the HomeScreen.html template
@app.get("/HomeScreen.html", response_class=HTMLResponse)
def home_screen(request: Request):
    return views.TemplateResponse("/HomeScreen.html", {"request": request})


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    Kitchen action routes

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# add an item (requests an item to be sent)
@app.post('/add_item')
def add_item(item:Item) -> dict:
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


# Run the FastAPI application
if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(app, host='192.168.0.34', port=8000)
    # uvicorn.run(app, host='100.80.240.83', port=8000)
    
    # 100.80.240.83
    uvicorn.run(app, host='0.0.0.0', port=8000)