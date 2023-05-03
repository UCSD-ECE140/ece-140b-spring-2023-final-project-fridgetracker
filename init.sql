-- fridge track database prototype 
-- subject to change with further planning

CREATE DATABASE if not exists FridgeTrackDB;
USE FridgeTrackDB;

DROP TABLE IF EXISTS User_Registry;
CREATE TABLE User_Registry (
    user_id integer AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(32) NOT NULL,
    last_name     VARCHAR(32) NOT NULL,
    email         VARCHAR(32) NOT NULL UNIQUE,
    user          VARCHAR(32) NOT NULL UNIQUE,
    pwd           VARCHAR(64) NOT NULL, -- since 'password' is a sql keyword
    kitchen_id    INT(8) NULL,
    user_role     INT(2) NULL
);

-- sample table named by kitchen_id
CREATE TABLE Kitchen_12345678 (
    section       VARCHAR(16) NOT NULL,
    item          VARCHAR(16) NOT NULL,
    added         timestamp NOT NULL,
    expiry        timestamp NOT NULL,
    -- optional data:
    shared        BOOL NULL,
    user_access   -- make this an array of user_role
);