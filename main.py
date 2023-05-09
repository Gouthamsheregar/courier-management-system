from flask import Flask
from mail import mail
from database import mysql
from admin import admin
from branch import branch
from courier import courier
from courier_boy import courier_boy
from customer import customer
import os


app = Flask(__name__)

# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'

try:
    app.config['MYSQL_DB'] = os.environ['CMS_DB_NAME']
    app.config['MYSQL_USER'] = os.environ['CMS_DB_USER']
    app.config['MYSQL_PASSWORD'] = os.environ['CMS_DB_PASS']
except KeyError:
    print('Please set database name, username and password as enviroment variables, follow steps in readme file for more info.')

app.secret_key='itsMySecretKey'
mysql.init_app(app)

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'courier2021response@gmail.com'
app.config['MAIL_PASSWORD'] = 'courier@2021'
app.config['MAIL_DEFAULT_SENDER'] = 'courier2021response@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

# blue_print registration
app.register_blueprint(admin)
app.register_blueprint(branch)
app.register_blueprint(courier)
app.register_blueprint(courier_boy)
app.register_blueprint(customer)

# starting the app
if __name__ == "__main__":
    app.run(port=2021, debug=True)

