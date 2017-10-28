######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
# Sarthak Jagetia aka DarkSeeker
# Aastha Jagetia aka PastaEater (love you :P)!
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this! #Fuck you! you change that!!:P

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sarthak' ##CHANGE YOUR PASSWORD WOMAN! (there are few more subtle hints everywhere like this...)
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email #you login through email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
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
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'> Information provided did not match - Try again! </a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['GET', 'POST'])
def register_user():
    # These are not requirements but if specified by user need to be added to the database.
    hometown = request.form.get('hometown')
    gender = request.form.get('gender')

    if request.form.get('first-name') == "" or request.form.get('last-name') == "":
        return flask.redirect(flask.url_for('register'))

    try:
        email = request.form.get('email')
        password = request.form.get('password')



        first_name = request.form.get('first-name')
        #print("first name: {0}" .format(first_name))

        last_name = request.form.get('last-name')
        dob = request.form.get('dob')

    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        query = "INSERT INTO Users(email, password, fname, lname, dob, hometown, gender) VALUES ('{0}', '{1}', '{2}','{3}', '{4}', '{5}', '{6}')".format(email, password, first_name, last_name, dob, hometown, gender)
        #print(cursor.execute("INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
        print(cursor.execute(query))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        #return render_template('email_exists.html')
        return flask.redirect(flask.url_for('email_exists'))

@app.route("/email_exists")
def email_exists():
    return render_template('email_exists.html')


def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Albums WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

import datetime as dt

@app.route('/add_album', methods=['GET','POST'])
@flask_login.login_required
def addAlbumName():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        #album_id = request.args.get('values')
        date_of_creation = dt.datetime.now()
        #uid = getUserIdFromEmail(flask_login.current_user.id)
        album_name = request.form.get('album')
        print(uid)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Albums (Name, date_of_creation, user_id) VALUES ('{0}', '{1}', '{2}' )".format(album_name, date_of_creation, uid))
        conn.commit()
        return render_template('hello.html', message='Added the album in your album list!')
    else:
        return render_template('add_album.html', albums= getUsersAlbums(uid))

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    '''
    Shortcomings: If a user inputs a wrong album name; the code breaks instead of throwing him a message that
    "No such album exists"...Need to nicely handle that exception

    Tags Create table has been modified; Has_tags table has been deleted and the Foreign key (picture_id) has
    been added now into Tags table

    Tags are taken input from the user as: #tag1 #tag2 #tag3
    '''
    tags_list =[]
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        tags = str(request.form.get('tags'))

        tags_list = tags.split('#') #I get first element of the list as '' hence I will skip over that when adding it to database
        tags_list = list(filter(None, tags_list))

        album_name = request.form.get('album')
        ab_name = str(album_name)

        photo_data = base64.standard_b64encode(imgfile.read())

        cursor = conn.cursor()
        cursor.execute("Select album_id FROM Albums AS a WHERE a.Name = '" + ab_name+ "'")
        album_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}','{3}' )".format(photo_data, uid, caption, album_id))
        conn.commit()

        ######TAGS PART HERE
        cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}' AND caption = '{1}' AND album_id = '{2}'" .format(uid, caption, album_id))
        photo_id = cursor.fetchone()[0]
        for i in tags_list:
            cursor.execute("INSERT INTO Tags (tag_word, picture_id) VALUES ('{0}', '{1}')" .format(i, photo_id ))
            conn.commit()
        ######TAGS PART END HERE

        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), albums= getUsersAlbums(uid))
    # The method is GET so we return a HTML form to upload the a photo.
    else:
        uid = getUserIdFromEmail(flask_login.current_user.id)
        return render_template('upload.html', photos=getUsersPhotos(uid), albums= getUsersAlbums(uid))


# end photo uploading code
#DELETING ALBUM AND PHOTOS

@app.route("/delete_album", methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
    '''
    Shortcomings:
    If there are no albums existing for a user in the database; this code still gives you a fake message of "Deleted!"
    for any album_name you input!
    '''
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        album_name = request.form.get('album')
        cursor = conn.cursor()
        print(album_name)
        print(type(album_name))
        ab = str(album_name)
        #cursor.execute("DELETE FROM Pictures AS p WHERE p.album_id = album_id")
        cursor.execute("DELETE FROM Albums WHERE Name ='" + ab + "'")
        conn.commit()
        return render_template('hello.html', message='Deleted!')
    else:
        return render_template('delete_album.html', albums=getUsersAlbums(uid))\

@app.route('/delete', methods=['POST'])
@flask_login.login_required
def delete_photos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    photo_id = request.args.get('p_id')
    print(photo_id)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
    conn.commit()
    #return render_template('hello.html', message='Deleted!')
    return render_template('upload.html', photos=getUsersPhotos(uid), albums= getUsersAlbums(uid))


#Friends functionality code

@app.route('/showallmakefriend', methods=['GET', 'POST'])
@flask_login.login_required
def showallUsers():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        cursor.execute("Select user_id, fname, lname FROM Users WHERE user_id <> '{0}'".format(uid))
        friend_tuple = cursor.fetchall()
        print(friend_tuple)
        return render_template("mke_friends.html", people=friend_tuple)
    else:
        return render_template("mke_friends.html")



@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def add_friend():
    '''
        Shortcomings: When user adds the same friend again it gives an Integrity error (error from database) since each
        must be able to add a friend only once.
        '''
    uid = getUserIdFromEmail(flask_login.current_user.id)
    uid2 = request.args.get('u_id')
    if request.method == 'POST':
        print(uid)
        print(uid2)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Friendship (UID1, UID2) VALUES ('{0}', '{1}')".format(uid, uid2))
        conn.commit()

        cursor = conn.cursor()
        cursor.execute("Select fname, lname FROM Users,Friendship WHERE Friendship.UID1 = '{0}' AND Friendship.UID2 = Users.user_id".format(uid))
        afriend = cursor.fetchall()
        return render_template("mke_friends.html", friends=afriend)

@app.route('/search_friend', methods=['GET', 'POST'])
@flask_login.login_required
def search_a_friend():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        searched_friend = str(request.form.get('srchfrnd'))
        print (searched_friend)
        name_list = searched_friend.split(' ')
        fname_friend = name_list[0]
        lname_friend = name_list[1]
        cursor = conn.cursor()
        cursor.execute("Select user_id, fname, lname FROM Users WHERE fname ='{0}' AND lname = '{1}'".format(fname_friend, lname_friend))
        searched_tuple = cursor.fetchall()

        cursor.execute("Select fname, lname FROM Users,Friendship WHERE Friendship.UID1 = '{0}' AND Friendship.UID2 = Users.user_id".format(uid))
        afriend = cursor.fetchall()
        #if (afriend):
        return render_template("mke_friends.html", searched_person=searched_tuple, friends=afriend)
        #else:
        #    return render_template("mke_friends.html", searched_person=searched_tuple)
    else:
        cursor = conn.cursor()
        cursor.execute("Select fname, lname FROM Users,Friendship WHERE Friendship.UID1 = '{0}' AND Friendship.UID2 = Users.user_id".format(uid))
        afriend = cursor.fetchall()
        return render_template("mke_friends.html", friends=afriend)

#Friend code ends here


#####################SEARCHING A USER'S UPLOADED PHOTOS BY TAGS###########################
@app.route('/search_by_tags',methods=['POST','GET'])
@flask_login.login_required
def search_by_tags():
    '''
    Shortcomings: If a user has not uploaded any photos, the page returns a blank page.
    NOTE: DEALT WITH THE ABOVE SHORTCOMING BELOW
    :return:
    '''
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT t.tag_word FROM Tags t WHERE t.picture_id IN (SELECT p.picture_id FROM Pictures p WHERE p.picture_id = t.picture_id AND p.user_id ='{0}')".format(uid))
    tags = cursor.fetchall()
    #print(type(tags))
    #print("_____")
    if(tags): #if tuple tags is not empty then render the page
        return render_template('search_by_tags.html', Tags = tags)
    else: #if empty then message the user to upload some photos first
        return render_template('search_by_tags.html', message="Upload a photo with some tags first!")

@app.route('/MyPhotoByTags')
def MyPhotoByTags():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    tag_word = request.args.get('tag_word_ToBePassed')
    cursor = conn.cursor()
    cursor.execute("SELECT p.picture_id, p.imgdata, p.caption FROM Pictures p WHERE p.picture_id IN(SELECT t.picture_id FROM Tags t WHERE t.tag_word = '{0}') AND p.user_id='{1}'".format(str(tag_word), uid))
    return render_template('search_by_tags.html', photos = cursor.fetchall())
##################### END ####################################

################# SEARCHING ALL PHOTOS BY EVERY USER WITH TAGS ###################











# default page
@app.route("/", methods=['GET'])
def homepage():
    return render_template('homepg.html', message='Welcome to Photoshare !')

@app.route("/hello", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welcome to Photoshare !')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
