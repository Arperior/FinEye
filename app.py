from flask import Flask, render_template, request, redirect,session
import mysql.connector

app = Flask(__name__)
app.secret_key ='aaaaa'
# MySQL configuration   #Sabka Apna Apna Password Daalna 
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="arib",
    database="project"
)
cursor = db.cursor()
# Basic Functions to be used
def get_users():
    cursor.execute("SELECT username FROM user")
    users = [user[0] for user in cursor.fetchall()]
    return users
def authenticate_user(username, password):  
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        session['username'] = username
        return True
    else:
        return False

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    else:
        return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/aboutus')
def aboutus():
    if 'username' in session:
        username = session['username']
        return render_template('about.html', username=username)
    else:
        return render_template('about.html')

@app.route('/transaction')
def transaction():
    if 'username' in session:
        username = session['username']
        return render_template('transaction.html', username=username)
    else:
        return render_template('transaction.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            return redirect('/')
        else:
            return redirect('/failed')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        income = request.form['income']
        
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        existing_username = cursor.fetchone()
        if existing_username:
            return 'Username already exists. Please choose a different username.'
        
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return 'Email already exists. Please use a different email.'
        
        cursor.execute("INSERT INTO user (username, email, password,total_income) VALUES (%s, %s, %s,%s)", (username, email, password,income))
        db.commit()
        
        session['username'] = username
        return redirect('/login')
    
    return render_template('signup.html')

@app.route('/failed')
def incorrect():
    render_template('failed.html')

@app.route('/view_tran')
def view_t():
    if 'username' in session:
        username = session['username']
        username = session['username']
        cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM transactions WHERE user_id = %s", (user_id,))
        transactions = cursor.fetchall()

        return render_template('view_tran.html', username=username,transactions=transactions)
    else:
        return redirect('/login')

@app.route('/submit', methods=['POST','GET'])
def submit():
    username = session['username']
    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]

    amount = request.form['amount']
    dot = request.form['dot']
    type = request.form['type']
    query = "INSERT INTO transactions (amount, date_transaction, type,user_id) VALUES (%s, %s, %s,%s)"
    values = (amount, dot, type,user_id)
    cursor.execute(query, values)
    db.commit()

    return redirect('/transaction')

if __name__ == '__main__':
    app.run(debug=True)
