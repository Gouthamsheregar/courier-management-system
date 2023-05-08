#imports-------------------------------------------------------------------------------------------------------
import email
from flask import Blueprint,render_template, request, redirect, url_for, session,flash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from database import mysql
from flask_mysqldb import MySQLdb
from mail import mail
from flask_mail import Message
import random

#create blueprint of customer------------------------------------------------------------------------------------
customer = Blueprint('customer', __name__, url_prefix='/', template_folder='templates',static_folder="static")

#main page index-------------------------------------------------------------------------------------------------
@customer.route('/')
@customer.route('/index')
def customer_index():
    return render_template('customer/index.html',contacts="none")


@customer.route('/search', methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        cid = request.form['cid']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM courier where tid={}".format(cid))
        user = curl.fetchone()
        curl.close()
        return render_template('customer/index.html',contacts=user)
    else:
        return redirect(url_for(".customer_index"))



@customer.route('/profile', methods=["GET", "POST"])
def profile():
    try:
        if request.method == 'POST':
            uid=session['email']
            
            nm = request.form['name']
            em = request.form['email']
            nu = request.form['phone']
            qs = request.form['question']
            aw = request.form['answer']

            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET name="{}",email="{}",phone="{}",question="{}",answer="{}"  WHERE email="{}"'.format(nm,em,nu,qs,aw,uid))
            mysql.connection.commit()
            cur.close()

            session['name'] = nm
            session['email'] = em
            session['phone'] = nu
            session['question'] = qs
            session['answer'] = aw
            
            flash('profile update successful','success')
            return redirect(url_for('.customer_index'))
        else:
            return redirect(url_for('.customer_index'))
    
    except:
        flash('email already exists','danger')
        return redirect(url_for('.customer_index'))

# customer registration----------------------------------------------------------------------------------------
@customer.route('/register', methods=["GET", "POST"]) 
def register():
    try:
        if request.method == 'GET':
            return render_template("customer/register.html")
        elif request.method == 'POST':
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM users")
            user = curl.fetchall()
            curl.close()
            if request.form['email'] == user:
                flash('Mail already exist')
                return redirect(url_for('customer.register'))
            else:
                name = request.form['name']
                email = request.form['email']
                phone = request.form['phone']
                password = request.form['password']
                question = request.form['question']
                answer = request.form['answer']

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (name,email,phone,password,question,answer) VALUES (%s,%s,%s,%s,%s,%s)",(name,email,phone,password,question,answer))
                mysql.connection.commit()
                cur.close()

                session['name'] = request.form['name']
                session['email'] = request.form['email']
                session['phone'] = request.form['phone']
                session['question'] = request.form['question']
                session['answer'] = request.form['answer']
                flash('register successful','success')
                return redirect(url_for('customer.customer_index'))
    except:
        flash('Mail already exist','warning')  
        return redirect(url_for('customer.register'))

# customer login---------------------------------------------------------------------------------------------------------
@customer.route('/cu_login',methods=["GET","POST"])
def cu_login():
    try:
        if request.method == 'POST':
            if request.form['email'] == "" and request.form['password'] == "":    
                flash('Email and Password cannot be empty','warning')
                return redirect(url_for('customer.cu_login'))
            elif request.form['email'] == "":    
                flash('Email cannot be empty','warning')
                return redirect(url_for('customer.cu_login'))    
            elif request.form['password'] == "":    
                flash('Password cannot be empty','warning')
                return redirect(url_for('customer.cu_login'))
            else:
                email = request.form['email']
                password = request.form['password']

                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM users WHERE email=%s",(email,))
                user = curl.fetchone()
                curl.close()

                if (user):
                    if  password == user["password"]:
                        session['name'] = user['name']
                        session['email'] = user['email']
                        session['phone'] = user['phone']
                        session['question'] = user['question']
                        session['answer'] = user['answer']
                        flash('log in successful','success')
                        return redirect(url_for('.customer_index'))
                        
                    else:
                        flash('Email and Password Not Match','danger')
                        return redirect(url_for('customer.cu_login'))
                else:
                    flash('user not found! please register.','warning')
                    return redirect(url_for('customer.cu_login'))

        else:
            return redirect(url_for('.customer_index'))
    except:
        flash("server busy, try again later...",'danger')
        return redirect(url_for('.customer_index'))
        

#reset password---------------------------------------------------------------------------------------------------
@customer.route('/reset_request',methods=["GET","POST"])
def reset_request():
    if request.method == 'GET' :
        return render_template("customer/reset_request.html")
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
                    curl.execute('UPDATE users SET password="{}" where email="{}"'.format(password,email))
                    mysql.connection.commit()
                    curl.close()
                    
                    flash('password updated','success')
                    return redirect(url_for('.customer_index'))
                else:
                    flash('invalid answer','danger')
                    return redirect(url_for('.reset_request'))
            else:
                flash('invalid question','danger')
                return redirect(url_for('.reset_request'))
        else:
            flash('email not found','danger')
            return redirect(url_for('.reset_request'))


#courier transaction---------------------------------------------------------------------------------------------
@customer.route('/transaction')
def transaction():
    phone = session['phone']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM courier where r_num="{}" or s_num="{}"'.format(phone,phone))
    data = cur.fetchall()
    cur.close()
    return render_template("customer/transaction.html",contacts=data)

# customer logout-----------------------------------------------------------------------------------------------
@customer.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('.customer_index'))
    

#customer_feedback---------------------------------------------------------------------------------------------------
@customer.route('/feedback', methods=["POST"])
def feedback():
    if request.method == 'POST':
        cid = ""
        email = request.form['email']
        message  = request.form['message']
        operation = 'feedback'
    
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO com_feed (cid, email, message, operation) VALUES (%s,%s,%s,%s)",(cid,email,message,operation,))
        mysql.connection.commit()
        cur.close()

        flash('feedback successful','success')
        return redirect(url_for('.customer_index'))

#customer_complaint---------------------------------------------------------------------------------------------------
@customer.route('/complaint', methods=["POST"])
def complaint():
    if request.method == 'POST':

        cid = request.form['cid']
        email = session['email']
        message  = request.form['message']
        operation = 'complaint'

        cur = mysql.connection.cursor()
        cur.execute("Select * from courier where tid={}".format(cid))
        data = cur.fetchone()
        cur.close()

        if (data):
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO com_feed (cid, email, message, operation) VALUES (%s,%s,%s,%s)",(cid,email,message,operation,))
            mysql.connection.commit()
            cur.close()
            flash('compalint sucssufull',"success")
            return redirect(url_for('.customer_index'))
        else:
            flash('Please Enter Valid Tracking ID.',"danger")
            return redirect(url_for('.customer_index'))


@customer.route('change_password',methods=['POST'])
def change_password():
    if request.method == 'POST':
        email = session['email']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        password = request.form['old_password']

        if (user):
            if password == user["password"]:
                new_password = request.form['new_password']
            
                cur = mysql.connection.cursor()
                cur.execute('UPDATE users SET password="{}" WHERE email="{}"'.format(new_password,email))
                mysql.connection.commit()
                cur.close()
                flash('password updated','success')
                return redirect(url_for('.customer_index'))
            else:
                flash('password not match, try again.','danger')    
                return redirect(url_for('.customer_index'))

    return redirect(url_for('.customer_index'))

@customer.route('/forget', methods=['POST','GET'])
def forget():
    if request.method == 'GET':
        return render_template('customer/otp.html')     
    else:
        email = request.form['email']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if (user):
            number = '1234567890'
            len= 6
            session['otp'] = "".join(random.sample(number,len))
            otp = session['otp']
            msg = Message('verification otp ',sender='courier2021response@gmail.com', recipients=[email])
            msg.body = f'''your verification code : {otp}
            thank you '''
            mail.send(msg)
            
            flash('otp send successfully','success')
            return render_template('customer/otp.html',otp=otp,email=email)
        else:
            flash('email not found.','danger')
            return redirect(url_for('customer.forget'))
        
@customer.route('/votp', methods=['POST','GET'])
def votp():
    if request.method=="POST":
        if request.form['OTP']==request.form['EOTP']:
            email = request.form['email']
            return render_template('customer/password.html',email=email)
        else:
            otp = request.form['EOTP']
            email = request.form['email']
            flash('worng otp','danger')
            return render_template('customer/otp.html',otp=otp,email=email)
    else:
        otp = session['otp']
        return render_template('customer/otp.html',otp=otp)

@customer.route('/change',methods=['POST'])
def change():
    if request.method == "POST":
        password = request.form['password']
        email = request.form['email']
        curl = mysql.connection.cursor()
        curl.execute('UPDATE users SET password="{}" where email="{}"'.format(password,email))
        mysql.connection.commit()
        curl.close()
        flash('password update successfull','success')
        return render_template('customer/index.html')




# end of code===================================================================================================
