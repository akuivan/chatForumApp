from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from db import db
from app import app

import users, messages, threads, categories

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forumIndex")
def forumIndex():
    return render_template("forumIndex.html")

@app.route("/ruokaCategory")
def ruoka_category():
    session["category"] = 1
    category_id= session["category"] 
    return render_template("category.html",threads=categories.fetch_category(category_id), admin = users.is_admin())

@app.route("/ohjelmointiCategory")
def ohjelmointi_category():
    session["category"] = 2
    category_id= session["category"] 
    return render_template("category.html",threads=categories.fetch_category(category_id), admin = users.is_admin())

@app.route("/muuCategory")
def muu_category():
    session["category"] = 3
    category_id= session["category"]
    return render_template("category.html",threads=categories.fetch_category(category_id), admin = users.is_admin())

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username,password):
            return redirect("/forumIndex")
        else:
            return render_template("error.html",message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
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
        if users.register(username,password):
            return redirect("/")
        else:
            session["password"]=password
            return render_template("error.html",message="Rekisteröinti ei onnistunut, " \
            "sillä kyseinen käyttäjätunnus on varattu tai syötit tyhjän lomakkeen")

@app.route("/newThread") 
def new_thread():
    list_of_users = users.get_list_of_users()
    return render_template("newThread.html", users = list_of_users)

@app.route("/createNewThread", methods=["POST"]) 
def create_new_thread():
    title = request.form["title"]
    private = request.form.getlist('private')
    selected = bool(private)
    category_id= session["category"] 
    username = session["username"]
    user_id = users.user_id()
    
    #create thread
    sql= "INSERT INTO threads (user_id, category_id, title, private, created_at)" \
    " VALUES  (:user_id , :category_id, :title, :private, NOW()) RETURNING id"
    db.session.execute(sql, {"user_id":user_id, "category_id":category_id, "title":title, "private":selected})
    db.session.commit()
    
    if selected: #thread is private       
        users.handle_allowed_users(request.form.getlist('user'), user_id, title)
        return redirect("/forumIndex")
    else:  #thread is public
        return redirect("/forumIndex")   

@app.route("/thread/<int:id>")
def thread(id):
    #check if thread is private
    sql = "SELECT private FROM threads WHERE id =:thread_id"
    result = db.session.execute(sql, {"thread_id":id})    
    private = result.fetchone()[0]
    session["thread"] = id

    if private:
        if users.check_permission_to_view_thread(users.user_id(), id):
            return threads.show_thread()
        else:
            return redirect("/forumIndex") 
    else: #thread is public
        return threads.show_thread()

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

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    if messages.send(content):
        return redirect("/forumIndex")
    else:
        return render_template("error.html",message="Viestin lähetys ei onnistunut")

@app.route("/deleteThread/<int:id>")
def delete_thread(id):
    users.delete_allowed_users_from_thread(id)
    messages.delete_all_messages_from_thread(id)
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

    return render_template("modifyThread.html", thread=list, id=id, allowed =users.get_list_of_allowed_users(id)
    , users = users.get_list_of_users())


@app.route("/updateThread/<int:id>", methods=["POST"])
def update_thread(id):
    private = request.form.getlist('private')
    selected = bool(private)

    sql = "UPDATE threads SET title=:title,private=:private WHERE id=:id"
    db.session.execute(sql, {"title":request.form["title"], "private":selected, "id":id})
    db.session.commit()

    if selected: #thread is private       
        users.update_allowed_users(request.form.getlist('user'))
        return redirect("/forumIndex")
    else:  #thread is public
        sql = "DELETE FROM allowedusers WHERE thread_id =:id"
        result = db.session.execute(sql,{"id":id})
        db.session.commit()
        return redirect("/forumIndex")


@app.route("/search", methods=["GET"])
def search_message():
    query = request.args["query"]
    sql = "SELECT thread_id, content, T.private FROM messages M, threads T WHERE M.thread_id=T.id" \
    " AND content LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()
    return render_template("result.html",messages=messages)