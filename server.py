from flask import Flask, render_template, flash, session, request, redirect, flash
from mysqlconfiguration import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app, 'wall_db')
app.secret_key = "dkdew23r20"
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/register')
def register():
    return render_template('registration.html')
@app.route('/registersubmit', methods = ['POST'])
def registersubmit():
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {
        'first_name': firstname,
        'last_name': lastname,
        'email': email,
        'password': password,
    }
    mysql.query_db(query, data)
    return redirect('/login')
@app.route('/login')
def login():
    return render_template('index.html')
@app.route('/loginsubmit', methods=['POST'])
def loginsubmit():
    email = request.form['email']
    password = request.form['password']
    query = "SELECT * FROM users WHERE email = :email"
    data = {'email':email}
    user = mysql.query_db(query, data)
    try:
        if user[0]['password'] == password:
            session['first_name'] = user[0]['first_name']
            session['id'] = user[0]['id']
        elif user[0]['password'] != password:
            flash("Please enter a valid email or password")
            return redirect('/login')
    except:
        flash("Please enter a valid email or password")
        return redirect('/login')
    return redirect('/the_wall')
@app.route('/the_wall')
def the_wall():
    messages = mysql.query_db("SELECT users.id AS users_id, users.first_name, users.last_name, messages.id AS message_id, messages.message, DATE_FORMAT(messages.created_at, '%M %e, %Y at %h:%i %p') as message_creation_date FROM users JOIN messages ON users.id = messages.user_id ORDER BY message_id DESC")
    comments = mysql.query_db("SELECT users.id AS user_id, users.first_name, users.last_name, comments.id AS comment_id, comments.comment, DATE_FORMAT(comments.created_at, '%M %e, %Y at %h:%i %p') as comment_creation_date, comments.message_id FROM users JOIN comments ON users.id = comments.user_id ORDER BY comment_id ASC")
    return render_template('the_wall.html', messages = messages, comments = comments)
@app.route('/logoff', methods=['POST'])
def logoff():
    return redirect('/login')
@app.route('/post', methods=['POST'])
def post():
    message = request.form['message']
    query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(), :user_id)"
    data = {
        'message': message,
        'user_id': session['id']
    }
    mysql.query_db(query, data)
    return redirect('/the_wall')
@app.route('/comment/<message_id>', methods=['POST'])
def comment(message_id):
    comment = request.form['postcomment']
    query = "INSERT INTO comments (comment, created_at, updated_at, message_id, user_id) VALUES (:comment, NOW(), NOW(), :message_id, :user_id)"
    data = {
        'comment': comment,
        'message_id': message_id,
        'user_id': session['id']
    }
    mysql.query_db(query, data)
    return redirect('/the_wall')
@app.route('/deletecomment', methods=['POST'])
def deletecomment():
    comment_id = request.form['comment']
    query = "DELETE FROM comments WHERE id = :id"
    data = {'id':comment_id}
    mysql.query_db(query, data)
    return redirect('/the_wall')
@app.route('/deletemessage', methods=['POST'])
def deletemessage():
    message_id = request.form['message_id']
    print message_id
    query = "DELETE FROM messages WHERE id = :id"
    data = {'id':message_id}
    try:
        mysql.query_db(query, data)
    except:
        pass
    return redirect('/the_wall')
app.run(debug=True)
