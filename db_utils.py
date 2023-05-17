''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
import mysql.connector as mysql                   # Used for interacting with the MySQL database
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials
import bcrypt
from datetime import datetime                     # to provide time and date

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration - TODO: figure out how pi will access credentials?
load_dotenv('credentials.env')             # Read in the environment variables for MySQL
db_config = {
  "host": os.environ['MYSQL_HOST'],
  "user": os.environ['MYSQL_USER'],
  "password": os.environ['MYSQL_PASSWORD'],
  "database": os.environ['MYSQL_DATABASE']
}
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# define helper functions for CRUD operations
# CREATE, SELECT, UPDATE, DELETE

# User registration
# CREATE user (user and kitchen profile (if setup))
def create_user(first_name:str, last_name:str, email:str, user:str, pwd:str, kitchen_id:int, user_role:int) -> int:
  pwd_encoded = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
  db = mysql.connect(**db_config)
  cursor = db.cursor()
  query = "insert into User_Registry (first_name, last_name, email, user, pwd, kitchen_id, user_role) values (%s, %s, %s, %s, %s, %s, %s, %s)"
  values = (first_name, last_name, email, user, pwd_encoded, kitchen_id, user_role)
  cursor.execute(query, values)
  db.commit()
  db.close()
  return cursor.lastrowid

def init_kitchen(kitchen_id:int) -> int:
  kitchen_id

# User login (authentification)
# TODO: sessions?


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Kitchen access (authorization)
# TODO: authorize the user before doing so.
# currently running on a local server with test kitchen so not implemented yet

# CREATE category (Fridge, freezer, pantry, counter, etc.)
def create_category(kitchen_id:int, section:str) -> bool:
  return False

# SELECT category - for accessing lists
# UPDATE category - for renaming categories...
# DELETE category - delete a category and all the food items...

def add_item(section:str, item:str, added, expiry) -> int:
  db = mysql.connect(**db_config)
  cursor = db.cursor()

  # TODO: accept specific kitchen names, needed after authentification
  query = "insert into kitchen_12345678 (section, item, added, expiry) values (%s, %s, %s, %s)"
  values = (section, item, added, expiry)
  cursor.execute(query,values)
  db.commit()
  db.close()
  return cursor.lastrowid


# crud operations, reuse for dealing with users/categories/food items? ie pass latter in as arg