from flask import Flask,render_template, request,session,url_for,redirect
from flask_mysqldb import MySQL
from datetime import datetime
 

def dbConnect():
    
    app = Flask(__name__)
    
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'foodgram'
    mysql = MySQL(app)
    cursor =mysql.connection.cursor()
    return cursor
    
