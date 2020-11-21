from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forumIndex")
def forumIndex():
    return render_template("forumIndex.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if login(username,password):
            return redirect("/forumIndex")
        else:
            return render_template("error.html",message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    #admin user's logout
    if not session.get("admin") is None:
        del session["username"]
        del session["admin"]
        return redirect("/")
    # normal user's logout
    else:
        del session["username"]
        return redirect("/")

@app.route("/createAccount")
def createAccountIndex():
    return render_template("createAccount.html")

@app.route("/registration", methods=["GET","POST"])
def createAccount():
    if request.method == "GET":
        return render_template("createAccount.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if register(username,password):
            return redirect("/")
        else:
            return render_template("error.html",message="Rekisteröinti ei onnistunut, sillä kyseinen käyttäjätunnus on varattu")

#
def login(username, password):
    sql = "SELECT password, id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[0],password):
            session["username"] = username
            # Check if user is admin
            if is_admin():
                session["admin"] = True
                #session["user_id"] = user[1]
                return True
            # Normal user
            else:
                return True
        #password doesn't match
        else:
            return False

def register(username,password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password,admin) VALUES (:username,:password,:admin)"
        db.session.execute(sql, {"username":username,"password":hash_value, "admin":False})
        db.session.commit()
        return True
    except:
        return False
    
def is_user():
    id = user_id()
    sql = "SELECT 1 FROM users WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    if result.fetchone()[0] != None:
        return True
    else:
        return False

def is_admin():
    id = user_id()
    sql = "SELECT admin FROM users WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    is_admin = result.fetchone()[0]
    return is_admin

def user_id():
    #fetch user's id by username
    username = session["username"]
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    return user_id

def checkPermissionToViewThread(user_id, thread_id ):
    # get user who created the thread
    sql = "SELECT user_id FROM threads WHERE id =:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id})    
    userWhoCreatedThread = result.fetchone()[0]

    if is_admin():
        return True
    elif is_user() and user_id == userWhoCreatedThread:
        return True
    elif is_user():
        sql = "SELECT 1 FROM allowedusers WHERE user1_id=:user1_id AND user2_id=:user2_id"
        result = db.session.execute(sql, {"user1_id":userWhoCreatedThread, "user2_id":user_id})
        print(userWhoCreatedThread)
        print(user_id)
        if result.fetchone() == None:    
            return False
        else:
            return True
    else:
        return False

def fetchCategory(category_id):
    sql = "SELECT threads.id, threads.title, threads.created_at FROM threads, categories WHERE threads.category_id = categories.id AND categories.id = :category_id"   
    result = db.session.execute(sql, {"category_id":category_id})
    return result.fetchall()

def thread_id ():
    return session["thread"]
#

@app.route("/ruokaCategory")
def ruokaCategory():
    session["category"] = 1
    category_id= session["category"] 
    return render_template("category.html",threads=fetchCategory(category_id))

@app.route("/ohjelmointiCategory")
def ohjelmointiCategory():
    session["category"] = 2
    category_id= session["category"] 
    return render_template("category.html",threads=fetchCategory(category_id))

@app.route("/muuCategory")
def muuCategory():
    session["category"] = 3
    category_id= session["category"]
    return render_template("category.html",threads=fetchCategory(category_id))

@app.route("/createNewThread", methods=["POST"]) 
def createNewThread():
    title = request.form["title"]
    private = request.form.getlist('private')
    selected = bool(private)
    category_id= session["category"] 
    username = session["username"]
    #fetch user's id by username
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    
    #create thread
    sql= "INSERT INTO threads (user_id, category_id, title, private, created_at) VALUES  (:user_id , :category_id, :title, :private, NOW()) RETURNING id"
    db.session.execute(sql, {"user_id":user_id, "category_id":category_id, "title":title, "private":selected})
    db.session.commit()
    
    if selected: #thread is private       
        allowed_users = request.form["allowed_users"]          
        usernames = [username.strip() for username in allowed_users.split(',')if username != '']  
        user1_id = user_id
        #fetch thread id
        sql = "SELECT id FROM threads WHERE title=:title"
        result = db.session.execute(sql, {"title":title})
        thread_id = result.fetchone()[0]

        #Check usernames from database
        for username in usernames:
            sql = "SELECT id FROM users WHERE username=:username"
            result = db.session.execute(sql, {"username":username})
            user2_id = result.fetchone()[0]
            #if user2_id exists in database
            if user2_id:
                #create table
                sql= "INSERT INTO allowedusers (thread_id, user1_id, user2_id) VALUES (:thread_id, :user1_id, :user2_id)"
                db.session.execute(sql, {"thread_id":thread_id,"user1_id":user1_id, "user2_id":user2_id})
                db.session.commit()

        return redirect("/forumIndex")
   
    else:  #thread is public
        return redirect("/forumIndex")

@app.route("/newThread") 
def newThread():
   return render_template("newThread.html")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    if send(content):
        return redirect("/forumIndex")
    else:
        return render_template("error.html",message="Viestin lähetys ei onnistunut")

def send(content):
    id = user_id()
    if user_id == 0:
        return False
    sql = "INSERT INTO messages (user_id, thread_id, content, sent_at) VALUES (:user_id, :thread_id, :content, NOW())"
    db.session.execute(sql, {"user_id":id, "thread_id":thread_id(),"content":content})
    db.session.commit()
    return True        

@app.route("/thread/<int:id>")
def thread(id):
    #check if thread is private
    sql = "SELECT private FROM threads WHERE id =:thread_id"
    result = db.session.execute(sql, {"thread_id":id})    
    private = result.fetchone()[0]
    session["thread"] = id

    if private:
        if checkPermissionToViewThread(user_id(), id):
            return render_template("thread.html")
        else:
            return redirect("/forumIndex") 
    else: #thread is public
        return render_template("thread.html")  