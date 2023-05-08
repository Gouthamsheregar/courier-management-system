# imports-----------------------------------------------------------------------------------------------------
from mail import mail
from flask import Blueprint,render_template, request, redirect, url_for, session,flash
from database import mysql
from flask_mail import Message
import random
from flask_mysqldb import MySQLdb

#creation of admin blueprint----------------------------------------------------------------------------------
admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates',static_folder='static')

#admin root page---------------------------------------------------------------------------------------------
@admin.route('/')
def admin_index():

    cur = mysql.connection.cursor()
    cur.execute('SELECT * from users')
    user = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from branchdb where status="accepted"')
    branch = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from courierboydb where status="accepted"')
    courierboy = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from courier')
    courier = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from com_feed where operation="feedback"')
    feedback = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from com_feed where operation="complaint"')
    complaint = cur.fetchall()
    cur.close()
    u = len(user)
    b = len(branch)
    cb = len(courierboy)
    c = len(courier)

    return render_template('admin/index.html',feedback=feedback,complaint=complaint,us = u ,bs= b ,cbs=cb ,cs=c,user=user,branch=branch,courierboy=courierboy,courier=courier)

#brach db----------------------------------------------------------------------------------------------------
@admin.route('/branchdb')
def branchdb():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM branchDb where status=""')
    data = cur.fetchall()
    cur.close()
    return render_template('admin/branchdb.html',contacts = data)

# existing branch--------------------------------------------------------------------------------------------
@admin.route('branch/existing_branch')
@admin.route('/existing_branch')
def existing_branch():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM branchDb where status="accepted"')
    data = cur.fetchall()
    cur.close()
    return render_template('admin/existing_branch.html',contacts = data)
# delete branch
@admin.route('admin/delete/<string:id>/<string:email>')
def delete_contact(id,email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE branchdb SET status="decline" WHERE id = {0}'.format(id))
    mysql.connection.commit()
    msg = Message('Hello',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = 'your application is decline.'
    mail.send(msg)
    return redirect(url_for('admin.existing_branch'))

# admin login------------------------------------------------------------------------------------------------
@admin.route('/admin/admin_login',methods=["GET","POST"])
@admin.route('/admin_login',methods=["GET","POST"])
def admin_login():
    admin_email = 'admin2021@gmail.com'
    admin_password = 'admin'
    admin_name = 'admin'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == admin_email and password == admin_password:
            session['name'] = admin_name
            session['email'] = admin_email
            flash('login successfully','success')
            return redirect(url_for('admin.admin_index'))
        else:
            flash('email and password not match','danger')
            return redirect(url_for('admin.admin_login'))
    else:
        return render_template("admin/admin_login.html")

# branch decline--------------------------------------------------------------------------------------------
@admin.route('admin/decline/<string:id>/<string:email>')
def decline_contact(id,email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('UPDATE branchdb SET status="decline" WHERE id = {0}'.format(id))
    mysql.connection.commit()

    msg = Message('Hello',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = 'your application is decline.'
    mail.send(msg)
    return redirect(url_for('admin.branchdb'))

# accept branch-------------------------------------------------------------------------------------------------------
@admin.route('admin/accept/<string:id>/<string:email>')
def accept(id,email):
    number = '1234567890'
    len= 10
    ran_num = "".join(random.sample(number,len))
    cur = mysql.connection.cursor()
    cur.execute('UPDATE branchdb SET status="accepted",random="{}" WHERE id={}'.format(ran_num,id))
    mysql.connection.commit()
    cur.close()

    msg = Message('Hello',sender='courier2021response@gmail.com', recipients=[email])
    msg.body = f'''your verification code : {ran_num}
        thank you for apply'''
    mail.send(msg)
    flash('branch accepted successfully','success')
    return redirect(url_for('admin.branchdb'))

@admin.route('admin/adminlogout')
def adminLogout():
    session.clear()
    return redirect(url_for('customer.customer_index'))

