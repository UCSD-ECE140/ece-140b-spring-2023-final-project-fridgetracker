# init_sample.py

import mysql.connector as mysql
import os
from dotenv import load_dotenv

load_dotenv("credentials.env")
db_host = os.environ['MYSQL_HOST']
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']

db =mysql.connect(user=db_user, password=db_pass, host=db_host)
cursor = db.cursor()

cursor.execute("CREATE DATABASE if not exists FridgeTrackDB;")
cursor.execute("USE FridgeTrackDB;")
cursor.execute("DROP TABLE IF EXISTS User_Registry;")
try: 
    cursor.execute("""
    CREATE TABLE User_Registry (
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
except RuntimeError as err:
    print("runtime error: {0}".format(err))


cursor.execute("DROP TABLE IF EXISTS kitchen01;")
try:
    cursor.execute("""
    CREATE TABLE kitchen01 (
        section       VARCHAR(16) NOT NULL,
        item          VARCHAR(16) NOT NULL,
        added         timestamp NOT NULL,
        expiry        timestamp NOT NULL
    );
    """)
    cursor.execute("insert into kitchen01 (section, item, added, expiry) value ('fridge', 'eggs', '2023-05-18 10:00:00', '2023-05-25 10:00:00')")
    cursor.execute("insert into kitchen01 (section, item, added, expiry) value ('fridge', 'rice', '2023-05-18 10:00:00', '2023-05-25 10:00:00')")
    cursor.execute("insert into kitchen01 (section, item, added, expiry) value ('fridge', 'bacon', '2023-05-18 10:00:00', '2023-05-25 10:00:00')")
except RuntimeError as err:
    print("runtime error: {0}".format(err))

db.commit()
db.close()