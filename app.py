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
# Aastha Anand aka PastaEater
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask.ext.login import current_user
import operator

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'sarthak' 
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
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
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
    tracker = 0
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

        photo_data = base64.standard_b64encode(imgfile.read()) #type string

        cursor = conn.cursor()
        cursor.execute("SELECT imgdata FROM Pictures AS p WHERE p.user_id = {0}".format(uid)) #a user cannot upload same photo twice
        imgdata_list = cursor.fetchall() #tuple
        for i in imgdata_list:
            for item in i:
                if (photo_data == str(item)):
                    print("Found a same photo")
                    tracker += 1
        if(tracker > 0):
            return render_template('upload.html', message="YOU CANNOT UPLOAD THE SAME PHOTO TWICE!", photos=getUsersPhotos(uid), albums= getUsersAlbums(uid))
        else:
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

@app.route('/see_all_photos')
def see_all_photos():
    cursor = conn.cursor()
    cursor.execute("SELECT album_id, name from albums")
    albaom = cursor.fetchall() #in her accent

    return render_template('see_all_photos.html', albums = albaom)

@app.route('/showallphotos')
def showallPhotos():
    album_id = request.args.get('values')
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
    allPhotos = cursor.fetchall()
    return render_template('see_all_photos.html', photos = allPhotos, album_id = album_id)

#Friends functionality code

@app.route('/showallmakefriend', methods=['GET', 'POST'])
@flask_login.login_required
def showallUsers():
    '''
        NotImplemented: Shows those users too who are already a friend of the logged in user.
    '''
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        cursor = conn.cursor()

        cursor.execute("Select fname, lname FROM Users,Friendship WHERE Friendship.UID1 = '{0}' AND Friendship.UID2 = Users.user_id".format(uid))
        afriend = cursor.fetchall()

        cursor.execute("Select user_id, fname, lname FROM Users WHERE user_id <> '{0}'".format(uid))
        friend_tuple = cursor.fetchall()
        print(friend_tuple)
        return render_template("mke_friends.html", people=friend_tuple, friends=afriend)
    else:
        cursor = conn.cursor()
        cursor.execute("Select fname, lname FROM Users,Friendship WHERE Friendship.UID1 = '{0}' AND Friendship.UID2 = Users.user_id".format(uid))
        afriend = cursor.fetchall()
        return render_template("mke_friends.html", friends=afriend)



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

# recommend friends to user
@app.route('/recommendfriends', methods=['GET', 'POST'])
@flask_login.login_required
def recommend_friends():
    '''If the users friend has no friend no suggestions are provided. User has to see all users add another friend to get suggestions'''

    uid = getUserIdFromEmail(flask_login.current_user.id)
    ff = []
    fof = []
    nf = []
    if request.method == 'POST':
        cursor = conn.cursor()
        cursor.execute("Select UID2 FROM Friendship WHERE UID1 = '{0}'".format(uid))
        my_friends = cursor.fetchall()
        for i in my_friends:
            ff.append(i[0])
        print(ff)
        if ff:
            for i in ff:
                cursor = conn.cursor()
                cursor.execute("Select UID2 FROM Friendship WHERE UID1 = '{0}'".format(i))
                friends_of_friends = cursor.fetchall()
                for m in friends_of_friends:
                    fof.append(m[0])
            print (fof)
            if fof:
                for item in fof:
                    cursor = conn.cursor()
                    print(item)
                    cursor.execute("Select user_id, fname,lname FROM Users WHERE user_id = '{0}' AND user_id <> '{1}'".format( item, uid))
                    names_of_friends = cursor.fetchall()
                    print (names_of_friends)
                    for n in names_of_friends:
                        nf.append(n)
                    print (nf)
                return render_template("mke_friends.html", suggestions=nf)
            else:
                return render_template("mke_friends.html", nofriends='true')
        else:
            cursor = conn.cursor()
            cursor.execute("Select user_id, fname, lname FROM Users WHERE user_id <> '{0}'".format(uid))
            names = cursor.fetchall()
            return render_template("mke_friends.html", suggestions=names)
    else:
        return render_template("mke_friends.html")
#Friend code ends here


#SEARCHING A USER'S UPLOADED PHOTOS BY TAGS
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
#END

#SEARCHING ALL PHOTOS BY EVERY USER WITH TAGS
@app.route('/search_allPhotos_by_tags',methods=['POST','GET'])
def search_allPhotos_by_tags():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT t.tag_word FROM Tags t WHERE t.picture_id IN (SELECT p.picture_id FROM Pictures p WHERE p.picture_id = t.picture_id)")
    tags = cursor.fetchall()
    #print(type(tags))
    #print("_____")
    if(tags): #if tuple tags is not empty then render the page
        return render_template('search_by_tags.html', All_Tags = tags)
    else: #if empty then message the user to upload some photos first
        return render_template('search_by_tags.html', message="No tagged photo uploaded by a user yet!")
#END

@app.route('/All_Photos_ByTags')
def All_Photos_ByTags():
    tag_word = request.args.get('tag_word_ToBePassed')
    cursor = conn.cursor()
    cursor.execute("SELECT p.picture_id, p.imgdata, p.caption FROM Pictures p WHERE p.picture_id IN(SELECT t.picture_id FROM Tags t WHERE t.tag_word = '{0}')".format(str(tag_word)))
    return render_template('search_by_tags.html', All_photos = cursor.fetchall())
#END

#SEARCHING PHOTOS BY POPULAR TAGS
@app.route('/by_Popular_tags', methods=['GET'])
def bypopulartags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag_word, COUNT(tag_word) FROM Tags GROUP BY tag_word ORDER BY COUNT(tag_word) DESC LIMIT 5")
	return render_template('search_by_tags.html', Popular_Tags=cursor.fetchall(), message1="Top 5 tags")
#END

@app.route('/Popular_Photos_ByTags')
def Popular_Photos_ByTags():
    tag_word = request.args.get('tag_word_ToBePassed')
    cursor = conn.cursor()
    cursor.execute("SELECT p.picture_id, p.imgdata, p.caption FROM Pictures p WHERE p.picture_id IN(SELECT t.picture_id FROM Tags t WHERE t.tag_word = '{0}')".format(str(tag_word)))
    return render_template('search_by_tags.html', Popular_photos = cursor.fetchall())
#END

#SEARCH A PHOTO BY TAG
@app.route('/search_photo_by_tag', methods=['GET', 'POST'])
def search_photo_by_tag():
    if request.method == 'POST':
        space = ''
        table_rename = []
        search = request.form.get('search')
        tag = [x.strip('#') for x in search.split(' ')]
        if space in tag:
            tag.remove('')
        query_string = 'SELECT p.imgdata, p.picture_id, p.caption FROM Pictures p WHERE p.picture_id IN( SELECT t1.picture_id FROM '
        count = 1
        for i in range(len(tag)):
            if (i < (len(tag) - 1)):
                query_string += ('Tags t' + str(count) + ', ')
                rename = 't' + str(count)
                table_rename.append(rename)
            else:
                query_string += ('Tags t' + str(count) + ' ')
                rename = 't' + str(count)
                table_rename.append(rename)
            count += 1
        query_string += 'WHERE '
        print(query_string)
        print(table_rename)
        # for j in range(len(tag)-2):
        for k in range(len(tag) - 1):
            query_string += table_rename[k] + '.picture_id =' + table_rename[k + 1] + '.picture_id AND '

        for m in range(len(tag)):
            if (m < (len(tag) - 1)):
                query_string += table_rename[m] + '.tag_word = ' + '\"' + tag[m] + '\"' + ' AND '
            else:
                query_string += table_rename[m] + '.tag_word = ' + '\"' + tag[m] + '\"' + ')'

        cursor = conn.cursor()
        cursor.execute(query_string)
        # cursor.fetchall()
        return render_template('search_photo_by_tag.html', All_photos=cursor.fetchall())
    # for k in range(len())
    else:
        return render_template('search_photo_by_tag.html')
#END


#Comments code
@app.route('/add_comment',methods=['POST'])
def add_comment():
    try:
        uid = getUserIdFromEmail(flask_login.current_user.id)
    except AttributeError:
        uid = 1  # GUEST USER

    picture_id = request.args.get('picture_id')
    comment_text = request.form.get('comment')
    print(picture_id)
    #print(comment_text)
    #print("____")
    cursor = conn.cursor()
    cursor.execute("SELECT p.picture_id FROM Pictures p WHERE p.user_id = '{0}'".format(uid))
    current_user_picture_id = cursor.fetchall()
    #print(current_user_picture_id)
    pid = []
    for i in current_user_picture_id: #converting from tuple to list
        pid.append(i[0])
        #print(i)
    print(pid)

    if int(picture_id) not in pid: #TO MAKE SURE USER DOESN'T COMMENT ON HIS OWN PICTURES
        cursor = conn.cursor()
        cursor.execute("INSERT INTO COMMENTS(text, date, user_id, picture_id) VALUES ('{0}','{1}','{2}','{3}')".format(comment_text, dt.datetime.now(), uid, picture_id))
        conn.commit()
        print('comment successful')
        return render_template('hello.html', message="You just commented on a photo!")
    else:
        print("own photo")
        return render_template('hello.html', error_message="You cannot comment on your own photo!")
#END


@app.route('/show_comments', methods=['POST'])
def show_comments():
    photo_id = request.args.get('picture_id')
    cursor = conn.cursor()
    cursor.execute("SELECT c.text,c.date,u.fname,u.lname from Comments c, Users u where c.user_id = u.user_id and c.user_id <> 1 and c.picture_id='{0}'".format(photo_id))
    reg_user = cursor.fetchall()
    cursor = conn.cursor()
    cursor.execute("SELECT c.text, c.date from Comments c where c.picture_id='{0}' AND c.user_id = 1".format(photo_id))
    guest = cursor.fetchall()
    return render_template('show_comments.html', display=reg_user, anon=guest)


#Likes starts here
@app.route('/likings', methods=['POST'])
def like_photos():
    '''
    Guest user has a hardcoded user_id of 1 and can like a photo once
    :return:
    '''
    try:
        uid = getUserIdFromEmail(flask_login.current_user.id)
    except AttributeError:
        uid = 1 #GUEST USER
    #print(uid)
    photo_id = request.args.get('p_id')
    #print(photo_id)
    date_of_like = dt.datetime.now()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Likes(user_id, picture_id, date_of_like) VALUES ('{0}','{1}', '{2}')".format(uid, photo_id, date_of_like))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(picture_id) FROM Likes WHERE picture_id = '{0}' GROUP BY picture_id".format(photo_id))
    no_of_likes = cursor.fetchall()
    print(no_of_likes)
    return render_template('hello.html', message="You liked a photo!")
#END


@app.route('/show_users_likes', methods=['POST'])
def show_users_likes():
    photo_id = request.args.get('values')
    cursor = conn.cursor()
    cursor.execute("SELECT u.fname,u.lname from Likes l, Users u where l.user_id = u.user_id and l.picture_id='{0}'".format(photo_id))
    reg_user = cursor.fetchall()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) from Likes l where l.picture_id='{0}' AND l.user_id = 1".format(photo_id))
    guest_user = cursor.fetchall()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) from likes l where l.picture_id='{0}'".format(photo_id))
    total_likes = cursor.fetchall()
    return render_template('likes.html', message="Here are the users who liked the selected photo!", display=reg_user, anon =guest_user, total =total_likes)

@app.route('/top_10_users')
def top_10_users():
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, fname, lname, email from Users where user_id <> 1")
    top10users = cursor.fetchall()
    print(top10users)
    user_activity = {}
    for i in top10users:
    	cursor = conn.cursor()
    	cursor.execute("SELECT count(*) from Pictures where user_id = {0}".format(i[0]))
    	photo_count = cursor.fetchall()[0]
    	cursor = conn.cursor()
    	cursor.execute("SELECT count(*) from Comments where user_id = {0}".format(i[0]))
    	comment_count = cursor.fetchall()[0]
    	print(comment_count[0],photo_count[0])
    	rank_count = int(comment_count[0]) + int(photo_count[0])
    	user_activity[str(i[1]+" "+i[2]+" "+i[3])] =rank_count
    user_activity = sorted(user_activity.items(), key=operator.itemgetter(1), reverse=True)
    user_activity = user_activity[0:11]
    return render_template('top_10_users.html', user_activity=user_activity)




# default page
@app.route("/", methods=['GET'])
def homepage():
    return render_template('homepg.html', message='Welcome to Photoshare !')

@app.route("/hello", methods=['GET'])
def hello():
    #uid = getUserIdFromEmail(flask_login.current_user.id)
    #print(uid)
    #print(type(uid))
    return render_template('hello.html', message='Welcome to Photoshare !')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
