import mysql.connector as mysql
import os
from dotenv import load_dotenv

load_dotenv("credentials.env")
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']

db = mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()

# Create the FridgeTrackDB database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS FridgeTrackDB;")
cursor.execute("USE FridgeTrackDB;")

# Create the User_Registry table
cursor.execute("DROP TABLE IF EXISTS User_Registry;")
cursor.execute("""
CREATE TABLE IF NOT EXISTS User_Registry (
    user_id integer AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(32) NOT NULL,
    last_name     VARCHAR(32) NOT NULL,
    email         VARCHAR(32) NOT NULL UNIQUE,
    user          VARCHAR(32) NOT NULL UNIQUE,
    pwd           VARCHAR(64) NOT NULL,
    kitchen_id    INT(8) NULL,
    user_role     INT(2) NULL
);
""")

# Create the kitchen01 table
cursor.execute("DROP TABLE IF EXISTS kitchen01;")
cursor.execute("""
CREATE TABLE IF NOT EXISTS kitchen01 (
    item_id integer AUTO_INCREMENT PRIMARY KEY,
    item          LONGTEXT NOT NULL,
    section       VARCHAR(16) NOT NULL,
    added         timestamp NOT NULL,
    expiry        timestamp NOT NULL
);
""")

db.commit()
db.close()
