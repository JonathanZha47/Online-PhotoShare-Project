######################################
# author ben lawson <balawson@bu.edu>
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
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
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
		cursor.execute("INSERT INTO Users (email, password, first_name, last_name, DOB, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password,firstname,lastname,DateofBirth,hometown,gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT aid, album_name, doc, user_id FROM Have_album WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() 

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUsersEmailFromID(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()
	
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
def getUsersNameFromID(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name FROM Users WHERE user_id = '{0}'".format(uid))
	firstName = cursor.fetchone()[0]
	cursor.execute("SELECT last_name FROM Users WHERE user_id = '{0}'".format(uid))
	lastName = cursor.fetchone()[0]
	return firstName+" "+lastName
#end login code
def getAlbumsnamefromaid(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Have_album WHERE aid = '{0}'".format(aid))
	return cursor.fetchall() 

@app.route('/profile')
@flask_login.login_required
def profile(): #profile
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		album_rename = request.form.get('album_rename')
		aid = request.form.get('aid')
		cursor=conn.cursor()
		if album_rename != None:
			#change the album's name
			cursor.execute("UPDATE Have_album SET album_name = '{0}' WHERE aid='{1}'".format(album_rename,aid))
			conn.commit()
			return render_template('hello.html', name=getUsersNameFromID(uid), message="here's your profile", albums = getUsersAlbums(uid), base64=base64)
		albumName = getAlbumsnamefromaid(aid)
		cursor.execute("DELETE FROM Have_album WHERE aid='{0}'".format(aid))
		conn.commit()
		return render_template('hello.html',name=flask_login.current_user.id, message='your album %s has been deleted!'%albumName,base64=base64)
	else:
		albums = getUsersAlbums(uid)
		return render_template('hello.html', name=getUsersNameFromID(uid), message="here's your profile", albums = albums, base64=base64)

@app.route("/addfriend", methods=['GET'])
def friends_add():
	return render_template('addfriend.html', supress='True')

@app.route('/addfriend',methods = ['POST'])
@flask_login.login_required
def addfriend():
		uid = getUserIdFromEmail(flask_login.current_user.id)
		friendemail = request.form.get('friend_email')
		f_uid = getUserIdFromEmail(friendemail)
		cursor = conn.cursor()
		if cursor.execute('''INSERT INTO Befriend (user_id, f_user_id, f_email) VALUES (%s, %s,%s)''', (uid,f_uid,friendemail)):
			conn.commit()
			cursor.execute('''INSERT INTO Befriend(user_id, f_user_id, f_email) VALUES (%s, %s, %s)''', (f_uid,uid,friendemail))
			conn.commit()
			return render_template('hello.html',name=flask_login.current_user.id, message='%s has been added as your friend'%getUsersNameFromID(f_uid), friend = getUsersNameFromID(f_uid), base64=base64)
		else:
			return render_template('addfriend.html',message="Friend already added or does not exist")


@app.route('/create',methods = ['Get','POST'])
@flask_login.login_required
def create():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		albumName = request.form.get('albumName')
		dateNow = datetime.date.today()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Have_album (album_name, doc, user_id) VALUES (%s, %s,%s)''', (albumName,dateNow,uid))
		conn.commit()
		return render_template('hello.html',name=flask_login.current_user.id, message='your album %s has been created'%albumName,base64=base64)
	else:
		return render_template('create.html')

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')

		

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)