from flask import Flask, render_template, request, redirect,session
import mysql.connector
from datetime import date,datetime

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
        balance = income

        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        existing_username = cursor.fetchone()
        if existing_username:
            return 'Username already exists. Please choose a different username.'
        
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            return 'Email already exists. Please use a different email.'
        
        cursor.execute("INSERT INTO user (username, email, password,total_income,balance) VALUES (%s, %s, %s,%s,%s)", (username, email, password,income,balance))
        db.commit()
        
        session['username'] = username
        return redirect('/login')
    
    return render_template('signup.html')

@app.route('/failed')
def incorrect():
    render_template('failed.html')

@app.route('/report_gen')
def report_gen():
    if 'username' in session:
        username = session['username']

        return render_template('report_gen.html', username=username)
    else:
        return render_template('report_gen.html')

@app.route('/gen_rep',methods=['POST','GET'])
def gen_rep():
    username = session['username']
    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.execute("select balance from user where user_id = %s",(user_id,))
    balance = cursor.fetchone()[0]

    start_str = request.form['Start']
    end_str = request.form['End']
    type = request.form['type']
    today = date.today()
    end = datetime.strptime(end_str, '%Y-%m-%d')
    start = datetime.strptime(start_str, '%Y-%m-%d')
    net_balance = balance
    expense = 0

    if type == 'All':
        cursor.execute("""
    SELECT t.amount, t.date_transaction
    FROM transactions t
    JOIN user u ON t.user_id = u.user_id
    WHERE u.user_id = %s
""", (user_id,))
        data= cursor.fetchall()
        for row in data:
            amt, dot = row
            dot_datetime = datetime.combine(dot, datetime.min.time())

            if start <= dot_datetime <= end:
                net_balance -= amt
                expense += amt
            else:
                pass
    query = "INSERT INTO report (total_expense,net_balance,date_of_report,user_id,start_date,end_date) VALUES (%s, %s, %s,%s,%s,%s)"
    values = (expense, net_balance, today,user_id,start,end)
    cursor.execute(query, values)
    db.commit()   

    return redirect('report_view')    

@app.route('/report_view',methods=['POST','GET'])
def display_report():
    if 'username' in session:
        username = session['username']
        cursor.execute("SELECT report_id,total_expense,net_balance,date_of_report,start_date,end_date FROM report")
        reports = cursor.fetchall()

        return render_template('report_view.html', reports=reports,username=username)
    else:
        return redirect('login.html')
    
@app.route('/view_tran')
def view_t():
    if 'username' in session:
        username = session['username']
        cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT transaction_id,amount,date_transaction,type FROM transactions WHERE user_id = %s", (user_id,))
        transactions = cursor.fetchall()

        return render_template('view_tran.html', username=username,transactions=transactions)
    else:
        return redirect('/login')

@app.route('/submit_t', methods=['POST','GET'])
def submit():
    username = session['username']
    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.execute("select balance from user where user_id = %s",(user_id,))
    balance = cursor.fetchone()[0]

    amount = request.form['amount']
    dot = request.form['dot']
    type = request.form['type']
    query = "INSERT INTO transactions (amount, date_transaction, type,user_id) VALUES (%s, %s, %s,%s)"
    values = (amount, dot, type,user_id)
    cursor.execute(query, values)
    net_balance = balance - amount
    cursor.execute("Update user set balance = %s where user_id = %s",(net_balance,user_id,))
    db.commit()

    return redirect('/view_tran')

@app.route('/show_balance',methods=['POST'])
def view_balance():
    if 'username' in session:
        username = session['username']
        cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        pressed = 1
        cursor.execute("Select balance from user where user_id=%s",(user_id,))
        balance = cursor.fetchone()[0]

        return render_template('index.html',pressed=pressed,balance=balance,username=username)

@app.route('/edit-existing_tran')
def transaction_edit():
    if 'username' in session:
        username = session['username']
        return render_template('edit-existing_tran.html', username=username)
    else:
        return render_template('edit-existing_tran.html')

@app.route('/update_t', methods=['Post','Get'])
def edit_transaction():
    username = session['username']
    cursor.execute("SELECT user_id FROM user WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.execute("select balance from user where user_id = %s",(user_id,))
    balance = cursor.fetchone()[0]

    amount = request.form['amount']
    tid = request.form['tid']
    type = request.form['type']

    cursor.execute("Select amount from transactions where transaction_id = %s",(tid,))
    current = cursor.fetchone()[0]
    cursor.execute("UPDATE transactions set amount=%s,type=%s where transaction_id=%s",(amount,type,tid,))
    new_balance = balance + current - amount
    db.commit()

    return redirect('/view_tran')

if __name__ == '__main__':
    app.run(debug=True)
