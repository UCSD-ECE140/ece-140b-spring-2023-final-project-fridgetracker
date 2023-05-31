from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt
import db_utils as db

# load credentials for connection to database
load_dotenv("../credentials.env")
db_config = {
    "host": os.environ['MYSQL_HOST'],
    "user": os.environ['MYSQL_USER'],
    "password": os.environ['MYSQL_PASSWORD'],
    "database": os.environ['MYSQL_DATABASE']
}

# Establish connection to the MySQL database
conn = mysql.connector.connect(**db_config)

# Create a FastAPI application
app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Define a Pydantic model for the item data
class Item(BaseModel):
    listTage: str
    itemName: str
    addedDate: str
    expiredDate: str


# Kitchen routes
@app.post('/add_item')
def add_item(item: Item):
    if db.add_item(item.listTage, item.itemName, item.addedDate, item.expiredDate):
        return {'message': 'Item added successfully'}
    return {'message': 'Item not added!'}


@app.get('/get_{category}_list')
def get_category_list(category: str) -> list:
    data = db.get_category(category)
    if data:
        return data


@app.delete('/delete_item')
def delete_item(item: Item):
    if db.delete_item(item.listTage):
        return {'message': 'Item deleted.'}
    return {'message': 'Item not deleted!'}


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
            return RedirectResponse(url='/HomeScreen.html')
    raise HTTPException(status_code=401, detail='Invalid username or password')


# Render the HomeScreen.html template
@app.get("/HomeScreen.html", response_class=HTMLResponse)
def home_screen(request: Request):
    return templates.TemplateResponse("HomeScreen.html", {"request": request})


# Run the FastAPI application
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)

# Close the database connection when the application shuts down
conn.close()
