from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from flask_sqlalchemy import SQLAlchemy

from db import db
from app import app

import messages

def thread_id ():
    return session["thread"]        


def show_thread():
    list = messages.get_list()
    return render_template("thread.html", count=len(list), messages=list, user_id=session["user_id"])

def fetch_category(category_id):
    sql = "SELECT threads.id, threads.title, threads.created_at FROM threads, " \
    "categories WHERE threads.category_id = categories.id AND categories.id = :category_id"   
    result = db.session.execute(sql, {"category_id":category_id})
    return result.fetchall()
