from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv
from flask_sqlalchemy import SQLAlchemy

from db import db
from app import app

import threads, users

def send(content):
    id = users.user_id()
    if users.user_id == 0:
        return False
    sql = "INSERT INTO messages (user_id, thread_id, content, sent_at) " \
    "VALUES (:user_id, :thread_id, :content, NOW())"
    db.session.execute(sql, {"user_id":id, "thread_id":threads.thread_id(),"content":content})
    db.session.commit()
    return True        


def get_list():
    sql = "SELECT M.content, U.username, M.sent_at, U.id, M.id FROM messages M, users U, threads T " \
          "WHERE M.user_id=U.id AND M.thread_id=T.id AND T.id=:input_id ORDER BY M.id"
    result = db.session.execute(sql,{"input_id":threads.thread_id()})
    return result.fetchall()    
    