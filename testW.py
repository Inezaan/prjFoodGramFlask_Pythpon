from flask import Flask,render_template, request,session,url_for,redirect,session,g,send_from_directory,Blueprint

testW=Blueprint("testW",__name__)

@testW.route('/welcome', methods = ['POST', 'GET'])
def welcome():
    if request.method == 'GET':
        if g.user:
            query_string="SELECT posts.postId,posts.FoodName,posts.Origin,posts.Description,posts.Date,posts.ReferUser,posts.Photo,users.userId,users.login FROM posts INNER JOIN users ON posts.referUser=users.userId"
            
            cursor = mysql.connection.cursor()
            cursor.execute(query_string)
            posts=cursor.fetchall()
            g.posts=posts
            return render_template('welcome.html',posts=posts ,user=session['login'])
        return redirect(url_for('login'))