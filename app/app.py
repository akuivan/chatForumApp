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
    del session["username"]
    del session["user_id"]
    #admin user's logout
    if not session.get("admin") is None:
        del session["admin"]
    return redirect("/")

@app.route("/createAccount")
def create_account_index():
    return render_template("createAccount.html")

@app.route("/registration", methods=["GET","POST"])
def create_account():    
    if request.method == "GET":
        # user has written username and/or password wrong when registering 
        # or submitted an empty form, and now returns from error.html back to create an account 
        if not session.get("password") is None:
            password = session["password"]
            del session["password"]
            return render_template("createAccount.html", password=password)
        else:
            return render_template("createAccount.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if register(username,password):
            return redirect("/")
        else:
            session["password"]=password
            return render_template("error.html",message="Rekisteröinti ei onnistunut, " \
            "sillä kyseinen käyttäjätunnus on varattu tai syötit tyhjän lomakkeen")

def login(username, password):
    sql = "SELECT password, id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[0],password):
            session["username"] = username
            session["user_id"] = user[1]
            # Check if user is admin
            if is_admin():
                session["admin"] = True
                return True
            # Normal user
            else:
                return True
        #password doesn't match
        else:
            return False

def register(username,password):
    if username == "" or password =="":
        return False
    else:
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

def check_permission_to_view_thread(user_id, thread_id ):
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

def fetch_category(category_id):
    sql = "SELECT threads.id, threads.title, threads.created_at FROM threads, " \
    "categories WHERE threads.category_id = categories.id AND categories.id = :category_id"   
    result = db.session.execute(sql, {"category_id":category_id})
    return result.fetchall()

def thread_id ():
    return session["thread"]

@app.route("/ruokaCategory")
def ruoka_category():
    session["category"] = 1
    category_id= session["category"] 
    return render_template("category.html",threads=fetch_category(category_id))

@app.route("/ohjelmointiCategory")
def ohjelmointi_category():
    session["category"] = 2
    category_id= session["category"] 
    return render_template("category.html",threads=fetch_category(category_id))

@app.route("/muuCategory")
def muu_category():
    session["category"] = 3
    category_id= session["category"]
    return render_template("category.html",threads=fetch_category(category_id))

@app.route("/createNewThread", methods=["POST"]) 
def create_new_thread():
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
    sql= "INSERT INTO threads (user_id, category_id, title, private, created_at)" \
    " VALUES  (:user_id , :category_id, :title, :private, NOW()) RETURNING id"
    db.session.execute(sql, {"user_id":user_id, "category_id":category_id, "title":title, "private":selected})
    db.session.commit()
    
    if selected: #thread is private       
        handle_allowed_users(request.form["allowed_users"], user_id, title)
        return redirect("/forumIndex")
    else:  #thread is public
        return redirect("/forumIndex")
        

def handle_allowed_users(allowed_users, user_id, title):
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

@app.route("/newThread") 
def new_thread():
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
    sql = "INSERT INTO messages (user_id, thread_id, content, sent_at) " \
    "VALUES (:user_id, :thread_id, :content, NOW())"
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
        if check_permission_to_view_thread(user_id(), id):
            return show_thread()
        else:
            return redirect("/forumIndex") 
    else: #thread is public
        return show_thread()

def show_thread():
    list = get_list()
    return render_template("thread.html", count=len(list), messages=list, user_id=session["user_id"])

def get_list():
    sql = "SELECT M.content, U.username, M.sent_at, U.id, M.id FROM messages M, users U, threads T " \
          "WHERE M.user_id=U.id AND M.thread_id=T.id AND T.id=:input_id ORDER BY M.id"
    result = db.session.execute(sql,{"input_id":thread_id()})
    return result.fetchall()    
    

@app.route("/deleteMessage/<int:id>")
def delete_message(id):
    sql = "DELETE FROM messages WHERE id=:id"
    result = db.session.execute(sql,{"id":id})
    db.session.commit()
    return redirect("/forumIndex")

@app.route("/modifyMessage/<int:id>")
def modify_message(id):
    sql = "SELECT content FROM messages WHERE id=:id" 
    result = db.session.execute(sql,{"id":id})
    content = result.fetchone()[0]

    return render_template("modifyMessage.html", content=content, id=id)

@app.route("/update/<int:id>", methods=["POST"])    
def update_message(id):
    sql = "UPDATE messages SET content=:content WHERE id=:id"
    db.session.execute(sql, {"content":request.form["content"], "id":id})
    db.session.commit()
    return redirect("/forumIndex")

@app.route("/deleteThread/<int:id>")
def delete_thread(id):
    sql = "DELETE FROM threads WHERE id=:id"
    result = db.session.execute(sql,{"id":id})
    db.session.commit()
    return redirect("/forumIndex")


@app.route("/modifyThread/<int:id>")
def modify_thread(id):
    sql = "SELECT U.username, T.title, C.title, T.private, T.created_at FROM threads T," \
    "users U, categories C WHERE T.user_id=U.id AND T.category_id = C.id AND T.id=:id" 
    result = db.session.execute(sql,{"id":id})
    thread = result.fetchall()
    list =thread

    return render_template("modifyThread.html", thread=list, id=id, allowed =get_list_of_allowed_users(id))

def get_list_of_allowed_users(id):
    sql = "SELECT username FROM users U, allowedusers A WHERE (U.id=A.user1_id OR U.id=A.user2_id) " \
    "AND A.thread_id =:id"
    result = db.session.execute(sql,{"id":id})
    allowed_users = result.fetchall()
    list = allowed_users
    
    return list

@app.route("/updateThread/<int:id>", methods=["POST"])
def update_thread(id):
    private = request.form.getlist('private')
    selected = bool(private)

    sql = "UPDATE threads SET title=:title,private=:private WHERE id=:id"
    db.session.execute(sql, {"title":request.form["title"], "private":selected, "id":id})
    db.session.commit()

    if selected: #thread is private       
        update_allowed_users(request.form["allowed_users"])
        return redirect("/forumIndex")
    else:  #thread is public
        sql = "DELETE FROM allowedusers WHERE thread_id =:id"
        result = db.session.execute(sql,{"id":id})
        db.session.commit()
        return redirect("/forumIndex")

def update_allowed_users(allowed_users):
    usernames = [username.strip() for username in allowed_users.split(',')if username != '']  

    #Check usernames from database
    for username in usernames:
        sql = "SELECT id FROM users WHERE username=:username"
        result = db.session.execute(sql, {"username":username})
        user2_id = result.fetchone()[0]
        #if user2_id exists in database
        if user2_id:
            #create table
            sql= "UPDATE allowedusers SET user2_id=:user2_id"
            db.session.execute(sql, {"user2_id":user2_id})
            db.session.commit()


@app.route("/search", methods=["GET"])
def search_message():
    query = request.args["query"]
    sql = "SELECT thread_id, content, T.private FROM messages M, threads T WHERE M.thread_id=T.id" \
    " AND content LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()
    return render_template("result.html",messages=messages)