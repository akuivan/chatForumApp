from flask import Flask
from flask import redirect, render_template, request, session, flash
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import app


db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")