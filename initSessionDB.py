import mysql.connector as mysql
import os
from dotenv import load_dotenv


# Read Database connection variables
load_dotenv("credentials.env")

db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']


# Connect to the db and create a cursor object
db = mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()


cursor.execute("CREATE DATABASE if not exists %s" % db_name)
cursor.execute("USE %s" % db_name)


cursor.execute("drop table if exists Sessions;")
try:
   cursor.execute("""
   CREATE TABLE Sessions (
       sessionId VARCHAR(32) NOT NULL PRIMARY KEY,
       email VARCHAR(30) NOT NULL,
       timeCreated datetime
    );
    """)
   db.commit()
except RuntimeError as err:
   print("runtime error: {0}".format(err))