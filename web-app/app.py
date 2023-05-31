from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os
import db_utils as db

# load credentials for connection to database
load_dotenv("../credentials.env")
db_config = {
    "host" : os.environ['MYSQL_HOST'],
    "user" : os.environ['MYSQL_USER'],
    "password" : os.environ['MYSQL_PASSWORD'],
    "database" : os.environ['MYSQL_DATABASE']
}

# Establish connection to the MySQL database
conn = mysql.connector.connect(**db_config)

# Create a FastAPI application
app = FastAPI()

# Define a Pydantic model for the item data
class Item(BaseModel):
    listTage: str
    itemName: str
    addedDate: str
    expierdDate: str

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# kitchen routes

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# add item to kitchen
@app.post('/add_item')
def add_item(item:Item):
    if (db.add_item(item.listTage, item.itemName, item.addedDate, item.expierdDate)):
        return {'message': 'Item added successfully'}
    return {'message': 'Item not added!'}

# get all items in list
@app.get('/get_{category}_list')
def get_category_list(category:str) -> list:
    data = db.get_category(category)
    if (data != []):
        return data
    
# delete an item by name
@app.delete('/delete_item')
def delete_item(item:Item):
    if (db.delete_item(item.listTage)):
        return {'message': 'Item deleted.'}
    return {'message': 'Item not deleted!'} 

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Login/Registration
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


# Run the FastAPI application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

# Close the database connection when the application shuts down
conn.close()
