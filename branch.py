# imports--------------------------------------------------------------------------------------------------------
from flask import Blueprint,render_template,request,redirect,url_for,session
from courier import courier
from flask.helpers import flash
from database import mysql
from mail import mail
from flask_mail import Message
from flask_mysqldb import MySQLdb
import random

# creation of branch blueprint-----------------------------------------------------------------------------------
branch = Blueprint('branch', __name__, url_prefix='/branch', template_folder='templates',static_folder="static")

# branch index --------------------------------------------------------------------------------------------------
@branch.route('/')
def branch_index():
    city = session['city']
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute('SELECT * FROM courier where (s_city="{}" and status="delivary placed") or status="{}"'.format(city,city))
    user = curl.fetchall()
    curl.close()
    
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute('SELECT * from branchdb')
    data = curl.fetchall()
    curl.close()

    return render_template('/branch/index.html',contacts=user, con=data)

@branch.route('branch/update_city',methods=["GET","POST"])
def update_city():
    if request.method == 'POST':
        tid = request.form['tid']
        city = request.form['city']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('UPDATE courier SET status="{}" where tid={}'.format(city,tid))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('branch.transaction'))
    else:
        return redirect(url_for('branch.branch_index'))
   


# existing courier boys-------------------------------------------------------------------------------------------
@branch.route('branch/existing_courierboy')
@branch.route('/existing_courierboy')
def existing_courierboy():
    city = session['city']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM courierboydb where city="{}" AND status="accepted"'.format(city))
    data = cur.fetchall()
    cur.close()
    return render_template('branch/existing_courierboy.html',contacts = data)

# [delete courier boys]
@branch.route('branch/delete/<string:id>/<string:email>')
def delete_contact(id,email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE courierboydb SET status="decline" WHERE id = {0}'.format(id))
    mysql.connection.commit()
    cur.close()

    msg = Message('Courier System response',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = "your account is decline ny branch"
    mail.send(msg)
    
    return redirect(url_for('branch.existing_courierboy'))

# branch login---------------------------------------------------------------------------------------------------
@branch.route('/branch/branch_login',methods=["GET","POST"])
@branch.route('/branch_login',methods=["GET","POST"])
def branch_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
 
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM branchdb WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()
 
        if (user):
            if password == user["password"]:
                session['first_name'] = user['first_name']
                session['email'] = user['email']
                session['city'] = user['city']
                session['phone'] = user['phone']
                session['password'] = user['password']
                session['address'] = user['address']
                session['question'] = user['question']
                session['answer'] = user['answer']
                session['random'] = user['random']
                session['status'] = user['status']
                return render_template("branch/index.html")
            else:
                flash('email and password not match','danger')
            return redirect(url_for('branch.branch_login'))
        else:
            flash('wrong email id','warning')
            return redirect(url_for('branch.branch_login'))
    else:
        return render_template("branch/branch_login.html")

# courierboys------------------------------------------------------------------------------------------------------
@branch.route('/courierBoys')
def courierBoys():
    city = session['city']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM courierboydb where city="{}" AND status=""'.format(city))
    data = cur.fetchall()
    cur.close()
    return render_template('branch/courierBoys.html',contacts = data)

# branch application----------------------------------------------------------------------------------------------
@branch.route('branch/branch_application',methods=["GET","POST"])
@branch.route('branch/branch/branch_application',methods=["GET","POST"])
@branch.route('branch/branch/branch/branch_application',methods=["GET","POST"])
def branch_application():
    try:
        if request.method == 'GET':
            return render_template("branch/branch_application.html")
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            address = request.form['address']
            question = request.form['question']
            answer = request.form['answer']
            city = request.form['city']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO branchDb (first_name,last_name,email,phone,password,address,city,question,answer) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(first_name,last_name,email,phone,password,address,city,question,answer))
            mysql.connection.commit()
            cur.close()
            flash('register successful','success')
            return redirect(url_for('branch.branch_login'))
    except:
        flash("email or phone number already exists.. plz check it and try again...",'danger')
        return redirect(url_for('branch.branch_application'))

# decline of courier boys application----------------------------------------------------------------------------
@branch.route('branch/decline/<string:id>/<string:email>')
def decline_contact(id,email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE courierboydb SET status="decline" WHERE id = {0}'.format(id))
    mysql.connection.commit()

    msg = Message('Hello',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = 'your application is decline by branch.'
    mail.send(msg)
    return redirect(url_for('branch.courierBoys'))

# accept of courier boys application----------------------------------------------------------------------------
@branch.route('branch/accept/<string:id>/<string:email>')
def accept(id,email):
    number = '1234567890'
    len= 6
    ran_num = "".join(random.sample(number,len))
    cur = mysql.connection.cursor()
    cur.execute('UPDATE courierboydb SET status="accepted",random="{}" WHERE id={}'.format(ran_num,id))
    mysql.connection.commit()
    cur.close()

    msg = Message('Hello',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = f'{ran_num}'
    mail.send(msg)

    return redirect(url_for('branch.courierBoys'))

# trancation---------------------------------------------------------------------------------------------------
@branch.route('/branch/transaction')
@branch.route('/transaction')
def transaction():

        city = session['city']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute('SELECT * FROM courier where s_city="{}" '.format(city))
        user = curl.fetchall()
        curl.close()
        return render_template('branch/transaction.html',contacts=user)

# reset password-------------------------------------------------------------------------------------------
@branch.route('/branch/reset_request')
def reset_request():
    if request.method == 'GET' :
        return render_template("branch/reset_request.html")
    else:
        email = request.form['email']
        question = request.form['question']
        answer = request.form['answer']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()


        if (user):
            if (question == user['question']):
                if answer == user['answer']:
                    curl = mysql.connection.cursor()
                    curl.execute('UPDATE branchdb SET password="{}" where email="{}"'.format(password,email))
                    mysql.connection.commit()
                    curl.close()
                    
                    flash('password updated','success')
                    return redirect(url_for('branch.branch_login'))
                else:
                    flash('invalid answer','danger')
                    return redirect(url_for('branch.reset_request'))
            else:
                flash('invalid question','danger')
                return redirect(url_for('branch.reset_request'))
        else:
            flash('email not found','danger')
            return redirect(url_for('branch.reset_request'))

@branch.route('branch/branch/resubmit', methods=["GET", "POST"])
def resubmit():
    try:
        if request.method == 'POST':
            id = session['email']
            nm = request.form['first_name']
            ls = request.form['last_name']
            em = request.form['email']
            pn = request.form['phone']
            ps = request.form['password']
            ct = request.form['city']
            addr = request.form['address']
            st = ""
            cur = mysql.connection.cursor()
            cur.execute('UPDATE branchdb SET first_name="{}",last_name="{}",email="{}",phone="{}",password="{}",city="{}",address="{}",status="{}"  WHERE email="{}"'.format(nm,ls,em,pn,ps,ct,addr,st,id))
            mysql.connection.commit()
            cur.close()
            session['first_name'] = nm
            session['last_name'] = ls
            session['email'] = em
            session['phone'] = pn
            session['password'] = ps
            session['address'] = addr
            session['city'] = ct
            session['status'] = st

            flash('profile update successful','success')
            return redirect(url_for('branch.resubmit'))
        else:
            return render_template('branch/index.html')
    except:
        flash('Mail already exist','warning')
        return redirect(url_for('branch.profile'))

@branch.route('branch/branch/verification', methods=["GET", "POST"])
@branch.route('branch/verification', methods=["GET", "POST"])
def verification():

    if request.method == 'POST':
        code = session['random']
        id = session['email']
        if request.form['random'] == code:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE branchdb SET random="" WHERE email="{}"'.format(id))
            mysql.connection.commit()
            cur.close()
            flash('verification successfull','success')
            return redirect(url_for('branch.branch_login'))
        else:
            flash('Code not match, try again...','danger')
            return redirect(url_for('branch.verification'))
    else:
        return redirect(url_for('branch.branch_index'))


# end of code==================================================================================================