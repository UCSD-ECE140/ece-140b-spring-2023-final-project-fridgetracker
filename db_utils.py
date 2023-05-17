''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
import mysql.connector as mysql                   # Used for interacting with the MySQL database
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials
import bcrypt
from datetime import datetime                     # to provide time and date

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration - TODO: figure out how pi will access credentials?
load_dotenv('public/credentials.env')             # Read in the environment variables for MySQL
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

# Kitchen access (authorization)
# CREATE category (Fridge, freezer, pantry, counter, etc.)
    # create food item may be called iteratively for reciept implementation in the future
# SELECT category
# UPDATE category
# DELETE

# crud operations, reuse for dealing with users/categories/food items? ie pass latter in as arg