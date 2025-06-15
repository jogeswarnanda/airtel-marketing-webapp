from flask import Flask, render_template,request, redirect, flash, url_for,session
from database import verify_login,add_user_to_db,fetch_upload_data,upload_data,update_user_to_db
import pandas as pd
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
import sys

db = SQLAlchemy() 
app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
# File upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("ver", sys.version)

# Define the model matching Excel structure
class UserUpload(db.Model):
    __tablename__ = 'user_uploads'

    upload_id = db.Column(db.String(50), primary_key=True)
    upload_mobile = db.Column(db.String(10))
    upload_name = db.Column(db.String(100))
    upload_month = db.Column(db.String(10))
    upload_role = db.Column(db.String(10))
    upload_fwa = db.Column(db.Integer)
    upload_jmnp = db.Column(db.Integer)
    upload_mnp =db.Column(db.Integer)
    upload_mdsso = db.Column(db.Integer)
    upload_simbilling = db.Column(db.Integer)


@app.route("/")
def hello_airtel():
    return render_template('home.html')

@app.route("/signup/",methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        s_mobile = request.form['s_mobile']
        s_name = request.form['s_name']
        s_role = request.form['s_role']
        admin_key = request.form['s_admin_key']
        print(s_mobile)
        print(s_name)
        data = request.form
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        amobile = " "
       
        if ( s_role == "Admin" ):
            if ( admin_key !="admin@1234"):
                flash("Admin key mandetory for Admin registration!", "waring")
            found_stat,dbpwd,name,role,amobile = verify_login(s_mobile, data, found_stat,dbpwd,name,role,amobile)
            if ( found_stat == "Y"):
                print("found post db call")
                flash("Mobile number Already exist!", "waring")
            else:
                add_user_to_db(data)
                flash("Admin Created !", "success")
        else:
            found_stat,dbpwd,name,role,amobile = verify_login(s_mobile, data, found_stat,dbpwd,name,role,amobile)
            print("found_stat:",found_stat)
            print("name:",name)
            print("role:",role)
            if ( found_stat == "Y"):
                print("found post db call")
                flash("Mobile number Already exist!", "waring")
            else:
                add_user_to_db(data)
                flash("User Created !", "success")
                # flash("Form submitted successfully!", "success")
                return redirect(url_for('signup_page'))
    return render_template('signup.html')

@app.route("/login/",methods=['GET', 'POST'])
def login_page():
    print("in login render")
    if request.method == 'POST':
        login_mobile = request.form['mobile']
        login_pwd    = request.form['password1']
        print(login_mobile)
        print(login_pwd)
        data = request.form
        found_stat = 'N'
        dbpwd  = " "
        name   = " "
        role   = " "
        amobile = " "
        found_stat,dbpwd,name,role,amobile = verify_login(login_mobile, data, found_stat,dbpwd,name,role,amobile)
        if found_stat == 'Y':
            if (login_pwd == dbpwd):
                print("matched pwd @@@")
                #session['mobile_session'] = login_mobile
                #session['mobile_session'] = login_mobile
                session['username'] = name   
                username = session['username']
                session['mobile'] = login_mobile
                mobile = session['mobile']   
                #session['username'] = role
                #username = session['username']
                 #return render_template("userdashboard.html",username=username)
                if  ( role == "Admin" ):
                    return admin_dashboard()
                else:
                    return user_dashboard()

            else:
                return render_template("login.html",
                               error="Invalid username or password")
        else:
            print("IN ELSE1 ", found_stat)
            return render_template("login.html",
                             error="User not found. Please register")
    else:
        return render_template('login.html')
    
@app.route("/userdashboard/")
def user_dashboard():
    dash_name = session['username']
    mobile = session['mobile'] 
    print("in user dashboard")
    print("seeess mob", session['mobile'])
    columns, rows = fetch_upload_data(mobile)

    #print("name", username)

    return render_template('userdashboard.html',username=dash_name,columns=columns,rows=rows)


@app.route("/admindashboard/")
def admin_dashboard():
    dash_name = session['username']
    mobile = session['mobile'] 
    print("in admin dashboard")
    print("seeess mob", session['mobile'])
    columns, rows = fetch_upload_data(mobile)
    #print("name", username)
    return render_template('admindashboard.html',username=dash_name)


#Logout route
@app.route("/logout/", methods=['GET', 'POST'])
def logout_page():
  print("LOGOUT")
  session.pop('username', None)
  session.clear()
  return redirect(url_for('login_page'))
  #return redirect(url_for('home'


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect('/')

    if file and file.filename.endswith(('.xlsx', '.xls')):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)

        # Optional: Preview in console
        print(df.head())

        # Iterate and insert into DB
        now = datetime.now()
        current_year = now.year
            
        for _, row in df.iterrows():
            print("excel rows ")
            print(row['Mobile_Number'])
            record = UserUpload(
            
            upload_mobile=row['Mobile_Number'],
            upload_name=row['Full_Name'],
            upload_month=row['Month'],
            upload_role=row['Role'],
            upload_fwa=row['LLM_FWA'],
            upload_jmnp=row['LLM_JMNP'],
            upload_mnp=row['LLM_MNP'],
            upload_mdsso=row['LLM_MDSSO'],
            upload_simbilling=row['LLM_Sim_Billing'],
            upload_id= str(row['Mobile_Number']) + "_" + str(row['Month']) + "_" + str(current_year)
            )
            print("rec", record.upload_id)
            print("rec", record.upload_mobile)
            upload_data(record)

        flash('Excel file uploaded and data saved to database!')
        return redirect('/admindashboard')

    else:
        flash('Invalid file type. Please upload .xlsx or .xls')
        return redirect('/admindashboard')
    
@app.route("/updateprofile/",methods=['GET', 'POST'])
def update_profile():
    prof_name = session['username']
    prof_mobile = session['mobile'] 
    print("in update profile")
    print("seeess mob", session['mobile'])
    print("seeess name", session['username'])
    #fetch_update_user(mobile)
    #print("name", username)
    amobile = " "   
    data = " "
    found_stat = 'N'
    name = " "
    role = " "
    dbpwd = " "
    found_stat,dbpwd,prof_name,role,prof_amobile = verify_login(prof_mobile, data, found_stat,dbpwd,name,role,amobile)
    print("prof a mob", prof_amobile)
    print("nnn", name)

    if request.method == 'POST':
        p_name = request.form['p_name']
        p_mobile = request.form['p_mobile']
        p_pmobile = request.form['p_pmobile']
        data = request.form
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        amobile = " "
       
        found_stat,dbpwd,name,role,amobile = verify_login(prof_mobile, data, found_stat,dbpwd,name,role,amobile)
        print("found_stat:",found_stat)
        print("name:",name)
        print("role:",role)
        if ( found_stat == "Y"):    
            update_user_to_db(data)
            flash("Data Updated!", "success")
                # flash("Form submitted successfully!", "success")
            return redirect(url_for('update_profile'))
            
    return render_template('updateprofile.html',prof_name=prof_name,prof_mobile=prof_mobile,
                           prof_amobile=prof_amobile)


print(__name__)
if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] =  "mysql+pymysql://4SzmE32uEz5t8DV.root:LCwy8CL3iWqMpxRD@gateway01.ap-southeast-1.prod.aws.tidbcloud.com/test?charset=utf8mb4"
    print("I am in if")
    app.run(host ='0.0.0.0',port=8080, debug=True)
    