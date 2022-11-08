CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;


CREATE TABLE IF NOT EXISTS  Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    DOB DATE ,
    hometown VARCHAR(255),
    gender CHAR(20),
    Contribution INT,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE IF NOT EXISTS Friends (
  f_user_id int4,
  f_email VARCHAR(255),
  PRIMARY KEY (f_user_id));
  
CREATE TABLE IF NOT EXISTS Befriend (
  user_id int4,
  f_user_id int4,
  f_email VARCHAR(255),
  PRIMARY KEY (user_id,f_user_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (f_user_id) REFERENCES Friends(f_user_id));
  
CREATE TABLE IF NOT EXISTS Likes (
  picture_id int4,
  User_id int4,
  PRIMARY KEY(picture_id,User_id),
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id),
  FOREIGN KEY(User_id) REFERENCES Users(User_id)
);


CREATE TABLE IF NOT EXISTS Albums (
    aid INT4 AUTO_INCREMENT,
    album_name VARCHAR(255),
    user_id int4,
    doc DATE,
    PRIMARY KEY (aid)
);


CREATE TABLE IF NOT EXISTS Have_album(
	aid int4 Auto_INCREMENT,
    user_id int4,
    album_name VARCHAR(255),
    doc DATE,
    PRIMARY KEY (aid,user_id),
    FOREIGN KEY (aid) REFERENCES Albums(aid),
    FOREIGN KEY (user_id) REFERENCES Users(user_id));

CREATE TABLE IF NOT EXISTS Contain_picture (
	picture_id int4,
    imgdata longblob ,
	caption VARCHAR(255),
    aid int4,
    PRIMARY KEY (aid, picture_id),
    FOREIGN KEY (aid) REFERENCES Albums(aid) 
    ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS Tags(
	word VARCHAR(255),
    PRIMARY KEY (word));
    
CREATE TABLE IF NOT EXISTS Hashtag (
	word VARCHAR(255),
    picture_id int4,
    PRIMARY KEY (picture_id,word),
    FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
    FOREIGN KEY (word) REFERENCES Tags(word));

CREATE TABLE IF NOT EXISTS Comments(
	cid int4 Auto_increment,
    comment_text VARCHAR(255),
    user_id int4,
    comment_date DATE,
    PRIMARY KEY (cid));
    
CREATE TABLE IF NOT EXISTS Leave_comment(
	user_id INT,
    cid int4 ,
    PRIMARY KEY (user_id, cid),
	FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (cid) REFERENCES Comments(cid));