######################################
# Author: Yiwei Zha <zhayiwei@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import email 
import flask
import time
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'JonathanWYDP3'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT pswd FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		firstname=request.form.get('firstname')
		lastname=request.form.get('lastname')
		DateofBirth=request.form.get('DateofBirth')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		cursor.execute("INSERT INTO Users (email, pswd, first_name, last_name, DOB, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password,firstname,lastname,DateofBirth,hometown,gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT p_data, pid, caption FROM Pictures WHERE uid = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getNameFromUserId(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT last_name FROM Users WHERE uid = '{0}".format(uid))
	return cursor.fetchone()[0]
	
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
def getTopContribute():
	cursor = conn.cursor()
	cursor.execute("SELECT *  FROM Users ORDER BY contribution DESC LIMIT 10")
	return cursor.fetchall()

def getTopTag():
	cursor = conn.cursor()
	cursor.execute("SELECT word, COUNT(*) FROM Tags GROUP BY word ORDER BY COUNT(*) DESC LIMIT 5")
	return cursor.fetchall()

def getUserTagsPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT Tags.tid, Tags.pid, Tags.word, Photos.pid, Photos.uid FROM Tags , PhotosP WHERE Tags.pid = Photos.pid AND Photos.uid = '{0}' GROUP BY Tags.word".format(uid)) 
	return cursor.fetchall()
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=getNameFromUserId(uid), message="here's your profile", photos = getUsersPhotos(uid), base64 = base64, tags = getUserTagsPhotos(uid))

def getAllAnounoumous(uid):
	#user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE uid != '{0}' AND uid NOT IN (SELECT Friends.uid2 FROM Friends  WHERE Friends.uid1 = '{0}')".format(uid))
	users = cursor.fetchall()
	res = []
	for user in users:
		if user[3] != 'UUUU@AAA':
			res.append(user)
	return res

def getAllfriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT Users.first_name, Users.last_name, Users.BOD, Users.hometown, Users.gender, Users.email, Friends.uid2 FROM Friends, Users WHERE Friends.uid1 = '{0}' AND Friends.uid2 = Users.uid".format(uid))
	return cursor.fetchall()

def getRecomFromFriends(uid):
	friends = getAllfriends(uid)
	friend_list = ()
	output = []
	for i in friends:
		friend_list = friend_list + getAllfriends(i[5])
	for s in friend_list:
		if s not in output and friends[5] != uid and s not in friends:
			output.append(s)
	return output

#friendpage
@app.route("/addfriend", methods=['GET','POST'])
@flask_login.login_required
def friends_add():
	uid1 = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'Post':
		uid2 = request.form.get('AddFriend')
		cursor = conn.cursor
		cursor.execute("INSERT INTO Friends uid1, uid2) VALUES ('{0}', '{1}')".format(uid1, uid2))
		conn.commit()
	return render_template('addfriend.html',anounoumous = getAllAnounoumous(uid1),friend = getAllfriends(uid2),friend_recom = getRecomFromFriends())

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def addTags(tags):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(pid) FROM Photos")
	pid = cursor.fetchone()[0]
	for tag in tags.split(', '):
		cursor.execute("INSERT INTO Tags (pid, word) VALUES ('{0}', '{1}')".format(pid, tag))
	conn.commit()

def getTags():
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT *  FROM Tags GROUP BY word") 
	return cursor.fetchall()

def getUserTags(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT Tags.tid, Tags.pid, Tags.word, Photos.pid, Photos.uid FROM Tags , Photos WHERE Tags.pid = Photos.pid AND Photos.uid = '{0}' GROUP BY Tags.word".format(uid)) 
	return cursor.fetchall()

def isAlbumExist(aid):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(aid) FROM Albums WHERE albums_id = '{0}' ".format(aid))
	num = cursor.fetchall()
	if num == ((1,),):
		return True
	else:
		return False

def isAlbumBelong(aid, uid):
		#use this to check if a email has already been registered
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(aid) FROM Albums WHERE aid = '{0}' AND uid = '{1}'".format(aid, uid))
	num = cursor.fetchall()
	if num == ((1,),):
		return True
	else:
		return False

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		tags = request.form.get('tag')
		album_id = request.form.get('album id')

		if isAlbumExist(album_id):
			print("Album Exist")
			if isAlbumBelong(album_id, uid):
				print("Album Belongs to Owner")	
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Photos (data, user_id, caption, albums_id) VALUES (%s, %s, %s, %s )''' ,(photo_data,uid, caption, album_id))
				cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE uid = '{0}'".format(uid))
				conn.commit()
				addTags(tags)
				print('upload successfully')
				return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
			else:
				print("Album does not belongs to owner")
				return render_template('hello.html')
		else:
			print("Album does not Exist")
			return render_template('hello.html')

def checkAllPhotos(word):
	cursor.execute("SELECT Photos.p_data, Photos.caption, Users.first_name, Users.last_name FROM Photos , Tags , Users  WHERE Photos.pid = Tags.pid AND Tags.word='{0}' AND Photos.uid = Users.uid".format(word))
	return cursor.fetchall()

@app.route('/tags', methods=['GET', 'POST'])
def tag():
	name = request.form.get('checkPhotos')
	return render_template('tags.html', tags = getTags(), photos=checkAllPhotos(name),base64=base64)

def checkUserPhotos(word):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT Photos.p_data, Photos.caption, Users.first_name, Users.last_name FROM Photos , Tags , Users  WHERE Photos.pid = Tags.pid AND Tags.word='{0}' AND Photos.uid='{1}' AND Photos.uid = Users.uid".format(word,uid))
	return cursor.fetchall()

app.route('/viewphotos', methods=['GET', 'POST'])
def viewphotos():
	name = request.form.get('checkPhotos')
	return render_template('viewphotos.html', photos=checkUserPhotos(name),base64=base64)

def searchTag(word):
	photo=()
	res = []
	for tag in word.split(' '):
		photo = photo + checkAllPhotos(tag)
	for i in photo:
		if i not in res:
			res.append(i)
	return res

@app.route("/tagsearch", methods=['GET', 'POST'])
def tag_search():
	if request.method == 'POST':
		if request.form.get('tag') is not None:
			tagstring = request.form.get('tag')
			return render_template('tagsearch.html', photos = searchTag(tagstring),base64=base64) 
	return render_template('tagsearch.html')

@app.route('/viewalbum', methods = ['Get'])
@flask_login.login_required
def viewmyphotos():
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT aid, album_name, creation_date FROM Albums WHERE uid = '{0}'".format(uid))
		album = cursor.fetchall()
		return render_template('viewalbum.html', album1 = album)

@app.route('/viewalbum', methods = ['Post'])
def SearchBYID1():
	try:
		aid =int(request.form.get('Album ID'))
	except:
		return render_template('hello.html', message = "Please login again")
	if isAlbumExist(aid):
		cursor = conn.cursor()
		cursor.execute("SELECT p_data, pid, caption FROM Photos WHERE aid = '{0}'".format(aid))
		photo = cursor.fetchall()
		return render_template('albumbyaid.html', photo_data=photo,base64=base64)
	else:
		return render_template('hello.html', message = "Please login again")


#ViewAllAlbums
@app.route('/viewallalbum', methods = ['Get'])
def viewallalbum():
		cursor.execute("SELECT Albums.aid, Albums.album_name, Albums.creation_date, Users.first_name Users.last_name FROM Albums, Users WHERE Albums.uid = Users.uid")
		album = cursor.fetchall()
		return render_template('viewallalbum.html', album2 = album)

@app.route('/createalbum', methods = ['Get','Post'])
@flask_login.login_required
def createalbum():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			album_name =request.form.get('album_name')
			birth_date=request.form.get('birth_date')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Albums (album_name, creation_date, uid) VALUE ('{0}', '{1}', '{2}')".format(album_name, birth_date, uid))
			conn.commit()
			return flask.redirect(flask.url_for('viewmyphotos'))
		except:
			return render_template('hello.html', message = "Failed, invalid input")
	else:
		return render_template('createalbum.html')


@app.route('/deletealbum', methods = ['Get','Post'])
@flask_login.login_required
def deletealbum():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			album_id =int(request.form.get('AlbumID'))
			if isAlbumBelong(album_id, uid):
				cursor = conn.cursor()
				cursor.execute("DELETE FROM Albums WHERE Albums.aid = '{0}'".format(album_id))
				conn.commit()
				return flask.redirect(flask.url_for('viewmyphotos'))
			else:
				return render_template('hello.html', message = "Failed, the album doesn't seems to belongs to you")
		except:
			return render_template('hello.html', message = "Failed, invalid input")
	else:
		return render_template('deletealbum.html')

	

@app.route('/deletephoto', methods = ['Get','Post'])
@flask_login.login_required
def deletephoto():
	if request.method == 'POST':	
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			pid =int(request.form.get('PhotoID'))
			cursor = conn.cursor()
			cursor.execute("DELETE FROM Photos WHERE Photos.pid = '{0}' AND Photos.user_id = '{1}'".format(pid, uid))
			conn.commit()
			return flask.redirect(flask.url_for('hello'))
		except:
			return render_template('hello.html', message = "Failed, wrong Photo ID")
	else:
		return render_template('deletephoto.html')
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT p_data, pid, caption FROM Photos")
	return cursor.fetchall()

def iflikedphoto(uid, sid):
	cursor = conn.cursor()
	cursor.execute("SELECT  COUNT(uid) FROM Likes WHERE uid = '{0}' AND pid = '{1}'".format(uid, sid))
	a = cursor.fetchall()
	if a == ((1,),):
		return True
	else:
		return False
def listlikedphoto(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Likes WHERE user_id = '{0}'".format(uid))
	list = cursor.fetchall()
	return list

@app.route('/likephotos', methods = ['Get', 'Post'])
@flask_login.login_required
def likePhotos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	pid= request.form.get('like')
	if request.method == 'POST':
		if iflikedphoto(uid, pid):
			return render_template('likephotos.html',likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)
		else:
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Likes(pid, uid) VALUES ('{0}', '{1}')".format(pid, uid))
			conn.commit()
			print("Liked")
		return render_template('likephotos.html',likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)
	else:
		return render_template('likephotos.html', likedlist = listlikedphoto(uid), photos = getAllPhotos(), base64 = base64)

def checkselfcomment(uid, pid):
	cursor = conn.cursor()
	cursor.execute("SELECT  COUNT(uid) FROM Photos WHERE uid = '{0}' AND pid = '{1}'".format(uid, pid))
	a = cursor.fetchall()
	print(a)
	if a == ((1,),):
		print("is my photo")
		return True
	else:
		print("not my photo")
		return False

def getUserIdByEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT uid FROM Users WHERE email = '{0}'".format(email))
	a = cursor.fetchall()
	print(a)
	return a[-1][0]

@app.route("/commentphoto", methods = ['POST', 'GET'])
def comment():
	if request.method == 'POST':
		pid = int(request.form.get("photoid"))
		c = request.form.get("commenting")
		try:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			if(checkselfcomment(uid, pid)):
				return render_template('hello.html', message = "Comment Prohibited")
			else:
				date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
				cursor = conn.cursor()
				cursor.execute("INSERT INTO Comments (pid, uid, C_text, Date_created) VALUES ('{0}', '{1}', '{2}', '{3}')".format(pid, uid, c, date ))
				cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE uid='{0}'".format(uid))
				conn.commit()
				print("Comment successfully")
				return render_template('hello.html', message = "Comment Successfully")
		except:
			print("Comment: Comment As a Guest")
			today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Users (email, pswd, first_name, last_name, contribution) VALUES ('UUUU@AAA', 'guest', 'Anonymous', 'User', '0')")
			conn.commit()
			
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Comments (pid, uid, C_text, Date_created) VALUES ('{0}','{1}', '{2}', '{3}')".format(pid, getUserIdByEmail("UUUU@AAA"), c, today ))
			conn.commit()
			return render_template('hello.html', message = "Comment Successfully As An Anonymous User")
	else:
		return render_template('commentphoto.html', photos = getAllPhotos(), base64 = base64)





@app.route("/commentdisplay", methods = ['POST', 'GET'])
def findcomment():
	if request.method == 'POST':
		pid = int(request.form.get("photoid"))
		print("Display Comments: Get PhotoID info")
		try:
			cursor = conn.cursor()
			cursor.execute("SELECT first_name, last_name, C_text FROM Users NATURAL JOIN (SELECT * FROM Comments  WHERE Comments.pid = '{0}') AS CC;".format(pid))
			a = cursor.fetchall()
			print("Display Comments: Get Comment info")
			print(a)
			return render_template('commentdisplay.html', photos = findphoto(pid) , base64 = base64, comments = a)
		except:

			return render_template('hello.html', message = "Failed")
	else:
		return render_template("commentdisplay.html")


def findphoto(pid):
		cursor = conn.cursor()
		cursor.execute("SELECT p_data, pid, caption FROM Photos WHERE pid = '{0}'".format(pid))
		return cursor.fetchall()

def cfind(text):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(uid) FROM Comments WHERE C_text = '{0}'".format(text))
	a = cursor.fetchall()
	if a == ((0,),):
		print("NO comment find")
		return False
	else:
		print("Find Comment")
		return True

@app.route("/searchcomment", methods = ["GET", "POST"])
def searchcomment():
	if request.method == "POST":
		try:
			text = request.form.get("commenttext")
			if cfind(text):
				cursor = conn.cursor()
				cursor.execute("SELECT Comments.uid, COUNT(*) AS comment_count, Users.first_name, Users.last_name, Users.uid  FROM Comments, Users WHERE C_text='{0}' AND Comments.uid = Users.uid GROUP BY Comments.uid ORDER BY comment_count DESC".format(text))
				print("sql conduct")
				l = cursor.fetchall()
				
				return render_template("searchcomment.html", comments = text, list = l)
			else:
				return render_template("searchcomment,html", res = " ")
		except:
			return render_template("hello.html", message = "Failed")
	else:
		return render_template("searchcomment.html")


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare',topContribute = getTopContribute(), topTag = getTopTag())


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
