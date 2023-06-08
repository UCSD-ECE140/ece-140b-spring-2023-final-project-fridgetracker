''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# db_utils.py
# helper functions for server to interact with database

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
import mysql.connector as mysql                   # Used for interacting with the MySQL database
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials
import bcrypt                                     # to encrypt/decrpyt passwords
from datetime import datetime                     # to provide time and date
from pydantic import BaseModel                    # to accept Items from server
# from flask import session
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
load_dotenv('credentials.env')             # Read in the environment variables for MySQL
db_config = {
  "host": os.environ['MYSQL_HOST'],
  "user": os.environ['MYSQL_USER'],
  "password": os.environ['MYSQL_PASSWORD'],
  "database": os.environ['MYSQL_DATABASE']
}

# Define a Pydantic model for the item data
class Item(BaseModel):
    listTage: str
    itemName: str
    addedDate: str
    expierdDate: str

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# define helper functions for CRUD operations
# CREATE, SELECT, UPDATE, DELETE

# User registration
# # CREATE user (user and kitchen profile (if setup))
# def create_user(first_name:str, last_name:str, email:str, user:str, pwd:str, kitchen_id:int, user_role:int) -> int:
#   pwd_encoded = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
#   db = mysql.connect(**db_config)
#   cursor = db.cursor()
#   query = "insert into User_Registry (first_name, last_name, email, user, pwd, kitchen_id, user_role) values (%s, %s, %s, %s, %s, %s, %s, %s)"
#   values = (first_name, last_name, email, user, pwd_encoded, kitchen_id, user_role)
#   cursor.execute(query, values)
#   db.commit()
#   db.close()
#   return cursor.lastrowid

# # initialize kitchen with first user signup
# def init_kitchen(kitchen_id:int) -> int:
#   return False

# # User login (authentification)
# # TODO: sessions
# def login_user(username: str, password: str) -> bool:
#     db = mysql.connect(**db_config)
#     cursor = db.cursor()
#     cursor.execute("SELECT pwd FROM User_Registry WHERE user = %s", (username,))
#     result = cursor.fetchone()
#     db.close()
    
#     if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
#         session['username'] = username
#         return True
    
#     return False

# # Verify if a user is logged in
# def is_user_logged_in() -> bool:
#     return 'username' in session

# # Get the currently logged-in user's username
# def get_logged_in_user() -> str:
#     return session.get('username', None)

# # Logout the user
# def logout_user() -> None:
#     session.pop('username', None)

# CREATE SQL query
def create_user(firstname:str, lastname:str, email:str, password:str) -> bool:
  try:
    db = mysql.connect(**db_config)
    cursor = db.cursor()
    query = "insert into Users (firstname, lastname, email, password) values (%s, %s, %s, %s)"
    values = (firstname, lastname, email, password)
    cursor.execute(query, values)
    db.commit()
    db.close()

  except Exception:
    print("Error:", e)
    return False

  return True

# SELECT SQL query
def select_user(email:str) -> tuple:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = f"select firstname, lastname, email from Users where email={email};"
  cursor.execute(query)
  result = cursor.fetchone()
  db.close()
  return result

# UPDATE SQL query
def update_user(firstname:str, lastname:str, email:str, password:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = "update Users set firstname=%s, lastname=%s, password=%s where email=`%s`;"
  values = (firstname, lastname, password, email)
  cursor.execute(query, values)
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

# DELETE SQL query
def delete_user(email:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  cursor.execute(f"delete from users where email={email};")
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

# SELECT query to verify password of users
def check_user_password(email:str, password:str) -> bool:
  db = mysql.connect(**db_config)
  print('checking')
  cursor = db.cursor()
  query = 'select password from Users where email=%s'
  cursor.execute(query, (email,))
  result = cursor.fetchone()
  cursor.close()
  db.close()

  if result is not None:
    return True if bcrypt.checkpw(password.encode('utf-8'), bytes(result[0])) else False
  return False

# CREATE SQL query
def create_session(sessionId:str, email:str) -> bool:
  try:
    db = mysql.connect(**db_config)
    cursor = db.cursor()
    query = "insert into Sessions (sessionId, email, timeCreated) values (%s, %s, %s)"
    values = (sessionId, email, datetime.utcnow())
    cursor.execute(query, values)
    db.commit()
    db.close()

  except Exception as e:
    print("Error:", e)
    return False

  return True

# SELECT SQL query
def select_session(sessionId:str) -> tuple:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = f"select * from Sessions where sessionId='{sessionId}';"
  cursor.execute(query)
  result = cursor.fetchone()
  db.close()
  return result

# DELETE SQL query
def delete_session(sessionId:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  cursor.execute(f"delete from Sessions where sessionId='{sessionId}';")
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Kitchen access (authorization)
# TODO: authorize the user before doing so.
def verify_user(user:int, kitchen_id:int) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  # query = f"select * from "
  db.close()
  return True if cursor.rowcount == 1 else False

# currently running on a local server with test kitchen so not implemented yet

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# CREATE section (Fridge, freezer, pantry, counter, etc.) -- TODO: determine if still needed
def create_category(kitchen_id:int, section:str) -> bool:
  return False

# SELECT section - for accessing lists
# def get_category(kitchen_id:int, section:str) -> list:
def get_category(section:str='') -> list:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  result = []
  query = ''
  if (section == ''):
    query = f"select item, added, expiry from kitchen01" # by default gets all the items
  else:
    query = f"select item, added, expiry from kitchen01 where section='{section}'"
  cursor.execute(query)
  result = cursor.fetchall()
  db.close()
  return result # result contains item, added, expiry

# UPDATE section - for renaming categories...
# DELETE section - delete a section and all the food items...

# TODO: verify timestamps from server -> db
def add_item(section:str, item:str, added:str, expiry:str) -> int:
  db = mysql.connect(**db_config)
  cursor = db.cursor()

  # TODO: accept specific kitchen names, needed after authentification -- currently using sample
  query = "insert into kitchen01 (section, item, added, expiry) values (%s, %s, %s, %s)"
  values = (section, item, added, expiry)
  cursor.execute(query,values)
  db.commit()
  db.close()
  return cursor.lastrowid # return item_id

# DELETE item
def delete_item(item:str, section: str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = f"delete from kitchen01 where item='{item}' and section='{section}';"
  cursor.execute(query)
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False

# UPDATE item -- rename or change add/expiration dates
def update_item(itemName:str, section:str, newName:str, newAdd:str, newExpire:str) -> bool:
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = f"update kitchen01 set item='{newName}', added='{newAdd}', expiry='{newExpire}' where item='{itemName}' and section='{section}'"
  cursor.execute(query)
  db.commit()
  db.close()
  return True if cursor.rowcount == 1 else False