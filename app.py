# Flask: python framework used in development of Web Application and WEb APIs, similar to django  

# Flask uses a single python file e.g, app.py to create the entire application where each component are separated by fuctions having its own route() 

# File structure: python file e,g app.py -> Create the backend logic  
# templates folder -> Used to house/hold all the html files (Front - End)
# static folder ->used to store all the resources e,g images, css, javascript...

# Modules : pythom files containing functions(lowercase) and classes(uppercase), inbuilt(random, math), user-define(lesson6c), external(flask)
# >> pip3 install modules
# decorators(@) -> injects functionality to a variable (object) 
# @variable.function()
# render_template(): use to return html files as server response
# jinja templates: Write python codes on html files(templates)
# sessions:identiify a user by the column names,username,email

from flask import Flask, render_template, request,redirect, session
import pymysql

connection = pymysql.connect(host='localhost', user='root', password='', database='kifaruDB')
print("Connection Successful")

# start
app = Flask(__name__)

# session secret key:session hijacking

app.secret_key = 'iotrhro4goqgonc3jieifirf7tr87rg'

@app.route('/')
def home():
    connection = pymysql.connect(host='localhost', user='root', password='', database='kifarudb')
    print("Connection Successful")

    # x category
    cursorX = connection.cursor()
    sqlX = 'select * from products where product_category = "x"'
    cursorX.execute(sqlX)
    x_items = cursorX.fetchall()

    # y category
    cursorY = connection.cursor()
    sqlY = 'select * from products where product_category = "y"'
    cursorY.execute(sqlY)
    y_items = cursorY.fetchall()

    # z category
    cursorZ = connection.cursor()
    sqlZ = 'select * from products where product_category = "z"'
    cursorZ.execute(sqlZ)
    z_items = cursorZ.fetchall()

    # a category
    cursor_A = connection.cursor()
    sql_A = 'select * from products where product_category = "a"'
    cursor_A.execute(sql_A)
    a_items = cursor_A.fetchall()

    return render_template('home.html', records = x_items, records2 = y_items, records3 = z_items, records4 = a_items)

@app.route('/single/<product_id>')
def single(product_id):
    connection = pymysql.connect(host='localhost', user='root', password='', database='kifaruDB')
    print("Connection Successful")

    cursor_single = connection.cursor()
    sql_single = 'select * from products where product_id = %s' 
    # Formating options(%s) -> 
    cursor_single.execute(sql_single, product_id)
    single = cursor_single.fetchone()
    print(single[4])

    # similar items based on category -> single[4]
    cursor_similar = connection.cursor()
    sql_similar = 'select * from products where product_category = %s'
    cursor_similar.execute(sql_similar, single[4])

    data = cursor_similar.fetchall()
    
    return render_template('single.html', single_record = single, similar = data)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        # server form validation: ensures we recieve the correct info
        # eliminate empties, correct phone number, password length, match
        # password length: password = "12345A"len(password) -> 6
        if len(password) < 8:
            return render_template('register.html', error_message = 'password Should be atleast 8 characters')
        elif password != confirm: 
            return render_template('register.html', error_message = 'Password Dont Match!!!')
        
        else:
            connection = pymysql.connect(host ='localhost', user='root', password='', database='kifaruDB')

            cursor_register = connection.cursor()
            sql_register = 'insert into users (username, email, phone, password) values (%s, %s, %s, %s)'
            cursor_register.execute(sql_register, (username, email, phone, password))

            # commit(): ensures that the table has been updated with the new record
            connection.commit()
            #send the sms to a registered user :phone
            #username,password
            from sms import send_sms
            send_sms(phone, f'thanks for registering ,your username is (username) and password is (password) keep it safe')

            return render_template('register.html', success_message = 'Registered Successfully')

    else: 
        return render_template('register.html')

# POST -> Sending inaformation(browser) to teh server 
# Get -> Receiving infromation (HTML)from the server 
@app.route('/login', methods =['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        connection = pymysql.connect(host='localhost', user='root', password='', database='kifaruDB')
        cursor_login = connection.cursor()
        sql_login ='select * from users where username = %s and password = %s'

        cursor_login.execute(sql_login, (username, password))

        # rowcount:counting the records on a table and return numeric value
        if cursor_login.rowcount == 0:
            return render_template('login,html ',error_message = 'invlaid credentials,Try Again!!!')
        else:
            session['key'] = username

            return redirect('/')


    else :
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'key' in session:
        session.clear()
        return redirect('/home')
    


import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/mpesa', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        # create an account on safaricom daraja
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "amount",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return '<h3>Please Complete Payment in Your Phone and we will deliver in minutes</h3>' \
               '<a href="/" class="btn btn-dark btn-sm">Back to Products</a>'    
    else:
        return render_template('single.html')

@app.route('/vendor', methods =  ['POST','GET'])
def vendor():
    if request.method == 'POST':
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        county = request.form["county"]
        password = request.form["password"]
        confirm = request.form['confirm']
        email = request.form["email"]

        if len(password) < 8:
            return render_template('vendor.html', error_message = 'password Should be atleast 8 characters')
        elif password != confirm: 
            return render_template('vendor``.html', error_message = 'Password Dont Match!!!')
        
        else:
            connection = pymysql.connect(host ='localhost', user='root', password='', database='kifarudb')

            cursor_vendor = connection.cursor()
            sql_vendor = 'insert into vendors (firstname, lastname, county, password,email) values (%s,%s,%s, %s, %s)'
            cursor_vendor.execute(sql_vendor, (firstname, lastname, county, password, email))

            # commit(): ensures that the table has been updated with the new record
            connection.commit()
            #send the sms to a registered user :phone
            #username,password

            return render_template('vendor.html', success_message = 'Registered Successfully')

    else: 
        return render_template('vendor.html')

app.run(debug=True)
# ends