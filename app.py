from flask import Flask,render_template, request,session,url_for,redirect,session,g,send_from_directory
from flask_mysqldb import MySQL
from datetime import datetime
from connexion import dbConnect
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from testW import testW

app = Flask(__name__)
app.secret_key=os.urandom(24)#session secret key

CORS(app)
#app.register_blueprint(testW,url_prefix="")


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'foodgram'

app.config['ALLOWED_EXTENSIONS']=['.jpg','.jpeg','.png']
app.config['UPLOAD_DIRECTORY']='pictures/'
mysql = MySQL(app)
#a globol list dict that contains the info of the loged in user
theUser =""
##################
#cursor = dbConnect();
@app.route('/')
def form():
    return render_template('login.html')
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    
    if request.method == 'GET':
        # return "Login via the login Form"
        return render_template('login.html')
    if request.method == 'POST':
        session.pop('userId',None)
        session.pop('login',None)
        login = request.form['login']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        
        query_string = "SELECT * FROM users WHERE login = %s AND password=%s"
        cursor.execute(query_string, (login,password,))
        
        result = cursor.fetchall()
        if len(result)==0:
            return "LOGIN NAME OR PASSWORD INCORRECT"
        else:
            session['userId']=result[0][0]
            session['login']=result[0][2]
            return redirect(url_for('welcome'))
            #return "here is userId "+ session['userId']
            #return redirect(url_for('welcome'))
@app.route('/logout')
def logout():
    session.pop('userId',None)
    session.pop('login',None)
    return render_template('login.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
       return render_template('register.html')
     
    if request.method == 'POST':
        # userId=request.form['userId']
        name = request.form['name']
        sex = request.form['sex']
        contact = request.form['contact']
        login = request.form['login']
        password = request.form['password']
        about = request.form['about']
        cursor = mysql.connection.cursor()
        
        #select all querry
        query_string = "SELECT * FROM users WHERE login = %s"
        cursor.execute(query_string, (login,))
        
        result = cursor.fetchall()  
        if len(result)==0:  #when the username doesn't exist already            
            cursor.execute("INSERT INTO users (name,login,sex,contact,about,password) VALUES (%s,%s,%s,%s,%s,%s)",
            (name,login,sex,contact,about,password))
            mysql.connection.commit()
            cursor.close()
            
            # cursor = mysql.connection.cursor()
            # query_string = "SELECT * FROM users WHERE login = %s"
            # cursor.execute(query_string, (login,))
            # result = cursor.fetchall()  
            # cursor.close()
            
            # cursor = mysql.connection.cursor()
            # cursor.execute("INSERT INTO relations(follower,followee) VALUES (%s,%s)",( result[0],result[0]))
            # mysql.connection.commit()
            return render_template('login.html')
        else:
            return "user name already taken. please use another one"
@app.route('/welcome', methods = ['POST', 'GET'])
def welcome():
    if request.method == 'GET':
        if g.user:
            query_string="SELECT posts.postId,posts.FoodName,posts.Origin,posts.Description,posts.Date,posts.ReferUser,posts.Photo,users.userId,users.login FROM posts INNER JOIN users ON posts.referUser=users.userId"
            
            cursor = mysql.connection.cursor()
            cursor.execute(query_string)
            posts=cursor.fetchall()
            
            #query_string = "SELECT * FROM relations WHERE follower =%s"
            query_string = "SELECT * FROM relations "
            #cursor.execute(query_string)
            user=session['userId']
            #cursor.execute(query_string,(user,))
            cursor.execute(query_string)
            relations=cursor.fetchall()
           
           #users
            query_string = "SELECT users.userId,users.login,relations.follower,relations.followee FROM users INNER JOIN relations ON users.userId=relations.followee"
            cursor.execute(query_string)
            user_relations=cursor.fetchall()
            
            print(user_relations)
            g.posts=posts
            return render_template('welcome.html',posts=posts,relations=relations,user=session['login'],userId=session['userId'])
        return redirect(url_for('login'))
@app.route('/post', methods=['POST'])
def addPost(): 
    if request.method == 'POST':
        foodname = request.form['foodname']
        origin = request.form['origin']
        description = request.form['description']
        photo=session['filename']
        postDate = datetime.now() 
        rUser=session['userId']
        cursor = mysql.connection.cursor()
                
        cursor.execute("INSERT INTO posts (foodname,origin,description,Date,ReferUser,photo) VALUES (%s,%s,%s,%s,%s,%s)",
        (foodname,origin,description,postDate,session['userId'],session['filename']))
        mysql.connection.commit()
        cursor.close()
                    #return "Done!!"
        #return render_template('welcome.html')
        return redirect(url_for('welcome',user=session['login']))
@app.route('/upload', methods=['POST','GET'])
def upload():
    file=request.files['picture']
    extension=os.path.splitext(file.filename)[1].lower()#getting the extension of the uploaded file being at the index 1 of the array result of the split
    if file:
        if extension not in app.config['ALLOWED_EXTENSIONS']:
            return 'The selected file is not an image...'
        file.save(os.path.join(
            app.config['UPLOAD_DIRECTORY'],
            secure_filename(file.filename)
        ))
       # print (g.posts)
        session['filename']=file.filename
        return render_template('welcome.html' ,picture=file.filename)
        #return redirect(url_for('welcome',picture=file.filename.))
    else:
        return redirect(url_for('welcome',user=session['login']))

@app.route('/cancel',methods=['POST','GET'])
def cancel():
    # file=request.files['picture']
    # file.delete(os.path.join(
    #         app.config['UPLOAD_DIRECTORY'],
    #         session['filename']
    #     ))
    return redirect(url_for('welcome'))
@app.before_request
def before_request():
    g.user=None
    if 'userId' in session:
        g.user=session['userId']


@app.route('/follow/<string:followee>',methods=['POST','GET'])
def follow(followee):
    follower=session['userId']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO relations(follower,followee) VALUES (%s,%s)",(follower,followee))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('welcome'))
@app.route('/serve-image/<filename>',methods=['GET'])
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_DIRECTORY'],filename)
#if __name__=='main':
app.debug=True
app.run(host='localhost', port=5000)