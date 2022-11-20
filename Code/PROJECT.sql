CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
SET GLOBAL sql_mode='';
    
CREATE TABLE USERS(
	uid INT AUTO_INCREMENT,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    DOB DATE NOT NULL,
    hometown VARCHAR(255),
    gender CHAR(20),
    pswd VARCHAR(255) NOT NULL,
    contribution INT NOT NULL DEFAULT '0',
    PRIMARY KEY (uid,email));

CREATE TABLE Friends (
	uid1 INTEGER,
	uid2 INTEGER,
	PRIMARY KEY (uid1, uid2),
	FOREIGN KEY (uid1)REFERENCES Users(uid),
	FOREIGN KEY (uid2)REFERENCES Users(uid));
    
CREATE TABLE Albums (
	aid INT AUTO_INCREMENT,
    album_name VARCHAR(255),
    uid INT NOT NULL,
    creation_date DATE,
    PRIMARY KEY (aid),
    FOREIGN KEY (user_id)REFERENCES Users(user_id));
    
CREATE TABLE Photos(
	pid INT AUTO_INCREMENT,
    caption VARCHAR(255),
    p_data LONGBLOB,
    aid INT,
    uid INT,
    PRIMARY KEY (pid),
    FOREIGN KEY (aid) REFERENCES Albums (aid) ON DELETE CASCADE,
	FOREIGN KEY (uid) REFERENCES Users (uid));

CREATE TABLE Tags(
	tid INT AUTO_INCREMENT,
    pid INT,
	word VARCHAR(255),
    PRIMARY KEY (tid),
	FOREIGN KEY (pid) REFERENCES Photos (pid) ON DELETE CASCADE);

CREATE TABLE Comments(
	cid INT NOT NULL,
    C_text VARCHAR(255),
    uid INT,
    pid INT,
    Date_created DATE,
    PRIMARY KEY (cid),
    FOREIGN KEY (uid)REFERENCES Users (uid),
	FOREIGN KEY (pid)REFERENCES Photos (pid));
    
CREATE TABLE Likes(
 pid INTEGER,
 uid INTEGER,
 PRIMARY KEY (pid,uid),
 FOREIGN KEY (pid)REFERENCES Photos (pid),
 FOREIGN KEY (uid)REFERENCES Users (uid));
								
                                         
    
	
    
    

						

