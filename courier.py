# imports--------------------------------------------------------------------------------------------
from MySQLdb import DATE
from flask import Blueprint,render_template,request,Response,redirect,flash,url_for
from database import mysql
import random
from datetime import date
from mail import mail
from flask_mail import Message
# creating of courier blueprint---------------------------------------------------------------------
courier = Blueprint('courier', __name__, url_prefix='/courier', template_folder='templates')

# courier deatil-----------------------------------------------------------------------------------
@courier.route('/courier_details',methods=["GET","POST"])
@courier.route('/courier/courier_details',methods=["GET","POST"])
def courier_details():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("select * from branchdb")
        branch = cur.fetchall()
        cur.close()
        print(branch)
        return render_template("courier/courier_details.html",branch=branch)
    else:
        number = '12345678901234567890'
        len= 10
        ran_num = "".join(random.sample(number,len))
        code = "".join(random.sample(number,6))
    
        Qty = request.form['Qty']
        del_type = request.form['del_type']
        ship_type = request.form['ship_type']
        weight = request.form['weight']
        
        s_name = request.form['s_name']
        s_num = request.form['s_num']
        s_email = request.form['s_email']
        s_add = request.form['s_add']
        s_city = request.form['s_city']
        s_state = request.form['s_state']
        s_zip = request.form['s_zip']
        
        r_name = request.form['r_name']
        r_num = request.form['r_num']
        r_email = request.form['r_email']
        r_add = request.form['r_add']
        r_city = request.form['r_city']
        r_state = request.form['r_state']
        r_zip = request.form['r_zip']

        
        price =  150 + int(weight) * 10
        status = 'delivary placed'
        dd = date.today()


        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO courier (tid,Qty,del_type,ship_type,weight,s_name,s_num,s_email,s_add,s_city,s_state,s_zip,r_name,r_num,r_email,r_add,r_city,r_state,r_zip,price,status,random) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(ran_num,Qty,del_type,ship_type,weight,s_name,s_num,s_email,s_add,s_city,s_state,s_zip,r_name,r_num,r_email,r_add,r_city,r_state,r_zip,price,status,code))
        mysql.connection.commit()

        cur = mysql.connection.cursor()
        cur.execute("select * from courier where tid={}".format(ran_num))
        data = cur.fetchone()
        cur.close()
        msg = Message('verification otp ',sender='courier2021response@gmail.com', recipients=[r_email,s_email])
        msg.body = f'''
            your tracking id is-{ran_num}
            your delivary otp code  is : {code}
            don't share with anyone
            thank you '''
        mail.send(msg)
        return render_template('courier/bill.html',contacts=data,d=dd)

# end of code=======================================================================================================================================