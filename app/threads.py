from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from flask_sqlalchemy import SQLAlchemy

from db import db
from app import app

import messages, users

def thread_id ():
    return session["thread"]        

def show_thread():
    list = messages.get_list()
    return render_template("thread.html", count=len(list), messages=list, user_id=session["user_id"], admin = users.is_admin())

def fetch_category_threads(category_id):
    sql = "SELECT  T.id, T.title, T.created_at, T.private, T.user_id FROM threads T, " \
    "categories C WHERE T.category_id = C.id AND C.id = :category_id"   
    result = db.session.execute(sql, {"category_id":category_id})
    return result.fetchall()