from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from db import db
from app import app


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

        if result.fetchone() == None:    
            return False
        else:
            return True
    else:
        return False

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

def get_list_of_allowed_users(id):
    sql = "SELECT username FROM users U, allowedusers A WHERE (U.id=A.user1_id OR U.id=A.user2_id) " \
    "AND A.thread_id =:id"
    result = db.session.execute(sql,{"id":id})
    allowed_users = result.fetchall()
    list = allowed_users
    
    return list


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
