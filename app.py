from flask import Flask, render_template,request, redirect, flash, url_for,session
from database import verify_login,add_user_to_db,fetch_upload_data,upload_data,update_user_to_db,db_leader_board,admin_update,create_audit,upload_pic_to_db,fetch_audit
import pandas as pd
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import sys
from dotenv import load_dotenv

load_dotenv()
db  = SQLAlchemy() 
app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
# File upload folder
UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)
today = date.today()
formatted_date = today.strftime("%d/%m/%Y")
current_datetime = datetime.now()
# Format the time as HH:MM:SS AM/PM
formatted_time = current_datetime.strftime("%I:%M:%S %p")

print("ver", sys.version)

# Define the model matching Excel structure
class UserUpload(db.Model):
    __tablename__ = 'user_uploads'

    upload_id         = db.Column(db.String(50), primary_key=True)
    upload_mobile     = db.Column(db.String(10))
    upload_name       = db.Column(db.String(100))
    upload_month      = db.Column(db.String(10))
    upload_role       = db.Column(db.String(10))
    upload_fwa        = db.Column(db.Integer)
    upload_jmnp       = db.Column(db.Integer)
    upload_mnp        = db.Column(db.Integer)
    upload_mdsso      = db.Column(db.Integer)
    upload_simbilling = db.Column(db.Integer)

#@app.route("/")
#def hello_airtel():
#    return login_page()
    #return render_template('login.html')

@app.route("/signup/",methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        s_mobile   = request.form['s_mobile']
        s_name     = request.form['s_name']
        s_role     = request.form['s_role']
        admin_key  = request.form['s_admin_key']
        print(s_mobile)
        print(s_name)
        data       = request.form
        found_stat = 'N'
        dbpwd      = " "
        name       = " "
        role       = " "
        amobile    = " "
        pic        = " "
       
        if ( s_role == "Admin" ):
            if ( admin_key !="admin@1234"):
                flash("Admin key mandetory for Admin registration!", "waring")
            found_stat,dbpwd,name,role,amobile,pic = verify_login(s_mobile, data, found_stat,dbpwd,name,role,amobile,pic)
            if ( found_stat == "Y"):
                print("found post db call")
                flash("Mobile number Already exist!", "waring")
            else:
                add_user_to_db(data)
                flash("Admin Created !", "success")
        else:
            found_stat,dbpwd,prof_name,role,prof_amobile,pic = verify_login(s_mobile, data, found_stat,dbpwd,name,role,amobile,pic)
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

@app.route("/",methods=['GET', 'POST'])
def login_page():
    print("in login render")
    if request.method == 'POST':
        login_mobile = request.form['mobile']
        login_pwd    = request.form['password1']
        login_role  = request.form['role1']
        print(login_mobile)
        print(login_pwd)
        data       = request.form
        found_stat = 'N'
        dbpwd      = " "
        name       = " "
        role       = " "
        amobile    = " "
        pic        = " "
        found_stat,dbpwd,name,role,amobile,pic = verify_login(login_mobile, data, found_stat,dbpwd,name,role,amobile,pic)
        if found_stat == 'Y':
            if (login_pwd == dbpwd):
                print("matched pwd @@@")
                #session['mobile_session'] = login_mobile
                #session['mobile_session'] = login_mobile
                if ( role == login_role ):
                    session['username'] = name   
                    if ( pic)   :
                        session['pic']  = "/"+pic
                    else:   
                        session['pic']  = "/static/uploads/blank_profile.jpg"
                    session['mobile']   = login_mobile
                    username            = session['username']
                    mobile              = session['mobile']   
                    #session['username'] = role
                    #username = session['username']
                    #return render_template("userdashboard.html",username=username)
                    if  ( role == "Admin" ):
                        return admin_dashboard()
                    else:
                        data_audit = [formatted_date, formatted_time, username, "Logged in"]
                        create_audit(data_audit)
                         
                        return user_dashboard()
                else:
                    flash("Invalid role selected", "danger")
                    return render_template("login.html",
                                   error="Invalid role selected")
            else:
                flash("Invalid username or password", "danger")
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
    if 'username' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login_page'))
    else:
        dash_name = session['username'] + "-" + "Dashboard"
        mobile    = session['mobile']
        session_mobile = mobile
        print("in user dashboard", mobile)
        #print("seeess mob", session['mobile'])
        columns, rows = fetch_upload_data(mobile)
        pic = session['pic'] 
        #print("pic >>", pic)
        #RANKING ::
        now = datetime.now()
        current_year = now.year
        current_month = now.strftime('%B')
        cm=current_month
        #print("current month", current_month)
        month_l1 = now - relativedelta(months=1)
        month_l2 = now - relativedelta(months=2)
        month_last1 = month_l1.strftime('%B')
        month_last2 = month_l2.strftime('%B')
        #print("cur month", current_month)
        #print("last ", month_last1.strftime('%B'))
        #print("prev m :", month_last2.strftime('%B'))
        
        #print("list main page :",list1)
        pic = session['pic']
        #print("pic:", pic)
        list1 = db_leader_board(current_month)
        results   = []
        for person in list1:
            mobile = person[0]
            name   = person[1]
            marks  = person[2:]
            total = sum(marks)
            results.append((mobile, name, total, marks))
        sorted_results1 = sorted(results, key=lambda x: x[2], reverse=True)
        l1 = len(sorted_results1)

        list2 = db_leader_board(month_last1)
        results   = []
        for person in list2:
            mobile = person[0]
            name   = person[1]
            marks  = person[2:]
            total = sum(marks)
            results.append((mobile, name, total, marks))
        sorted_results2 = sorted(results, key=lambda x: x[2], reverse=True)
        l2 = len(sorted_results2)

        list3 = db_leader_board(month_last2)
        results   = []
        for person in list3:
            mobile = person[0]
            name   = person[1]
            marks  = person[2:]
            total = sum(marks)
            results.append((mobile, name, total, marks))
        sorted_results3 = sorted(results, key=lambda x: x[2], reverse=True)
        l3 = len(sorted_results3)
        
        print(f"session_mobile:" , session_mobile)
        print(f"sorted res curr month::", sorted_results1)
        print(f"sorted res len::", l1)

        #position1
        position1 = position = next((i for i, entry in enumerate(sorted_results1) if entry[0] == session_mobile), -1)
        position1 = position1 + 1  # To make it 1-based index
        print(f"position in curr month::", position1)

        print(f"sorted res last month::", sorted_results2)
        print(f"sorted res len::", l2)
        #position2 
        position2 = position = next((i for i, entry in enumerate(sorted_results2) if entry[0] == session_mobile), -1)
        position2 = position2 + 1  # To make it 1-based index
        print(f"position in prev month::", position2)

        print(f"sorted res last month::", sorted_results3)
        print(f"sorted res len::", l3)
        

        #position3  
        position3 = position = next((i for i, entry in enumerate(sorted_results3) if entry[0] == session_mobile), -1)
        position3 = position3 + 1  # To make it 1-based index
        print(f"position in prev prev month::", position3)

        r_columns  = [month_last2, month_last1, current_month+"(MTD)"]
        r_rows     = [(str(position3),str(position2),str(position1))] 


        return render_template('userdashboard.html',username=dash_name,columns=columns,rows=rows,prof_pic=pic,r_columns=r_columns,r_rows=r_rows)


@app.route("/admindashboard/", methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login_page'))
    #elif request.method == 'POST':  
       #    print("in admin dashboard post")
       #    dash_name = session['username'] 
       #    admin_option = 's'
       #    data = request.form 
    else:
        dash_name = session['username']
        users           = " "
        mobile          = " "
        if ( request.method == 'POST' ) and request.form.get('update'):
            print("in admin dashboard post update")
            users = request.form
            print("users bef updated in admin", users)
            admin_option = 'u'
            users_updated = admin_update(users,admin_option,mobile)
            print("users updated in admin", users_updated)
            flash("User Data Updated !", "success")
            users = " "
            mobile = " "
            admin_option = 's'
            users_updated2 = admin_update(users,admin_option,mobile)
            for user in users_updated2:
                print("user in admin", user)
            return render_template('admindashboard.html',username=dash_name,users =users_updated2)
            
            #return render_template('admindashboard.html',username=dash_name,users =users_updated)
         
        else:
            print("in admin dashboard get")
            #print("request.method",request.method)
            #dash_name = session['username']
            #mobile = session['mobile'] 
            #print("in admin dashboard")
            #print("seeess mob", session['mobile'])
            dat = " "
            auditr = fetch_audit(dat)

            admin_option = 's'
            users_updated = admin_update(users,admin_option,mobile)
            for user in users_updated:
                print("user in admin", user)
        return render_template('admindashboard.html',username=dash_name,users =users_updated,auditr=auditr)
    
        #print("name", username)
        #    name = request.form['name']
        #    role = request.form['role']
        #    password = request.form['password']
        #    db_admin_update(mobile)
        #    return redirect(url_for('admindashboard'))
        #return render_template('admindashboard.html',username=dash_name)
     
#Logout route
@app.route("/logout/", methods=['GET', 'POST'])
def logout_page():
  print("LOGOUT")
  username = session['username']
  data_audit = [formatted_date, formatted_time, username, "Logged Out"]
  create_audit(data_audit)

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
        current_month = now.month
        month_last1 = now - relativedelta(months=1)
        month_last2_= now - relativedelta(months=2)
        print(current_month)
        print(month_last1)
        print(month_last1)
            
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
    
@app.route('/uploadpic', methods=['POST'])
def upload_pic():
    print("in upload pic")
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect('/')

    if file and file.filename.endswith(('.jpg','.jpeg','.png')):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)
        mobile = session['mobile']
        print("mobile in upload pic", mobile)
        # Optional: Preview in console
        print(df.head())
        # Iterate and insert into DB
        upload_pic_path = filepath
        upload_pic_to_db(mobile,upload_pic_path)

        flash('Pic uploaded and data saved to database!')
        return redirect('/updateprofile')

    else:
        flash('Invalid file type. Please upload .jpg or .jpeg or .png')
        return redirect('/updateprofile')
    
    
@app.route("/updateprofile/",methods=['GET', 'POST'])
def update_profile():
    if 'username' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login_page'))
    prof_name = session['username']
    prof_mobile = session['mobile'] 
    prof_pic = session['pic']
    print("in update profile")
    print("seeess mob", session['mobile'])
    print("seeess name", session['username'])
    print("seeess pic ", session['pic'])
    #fetch_update_user(mobile)
    #print("name", username)
    dash_name = "Welcome, " + session['username'] 
    amobile = " "   
    data = " "
    found_stat = 'N'
    name = " "
    role = " "
    dbpwd = " "
    pic = ""
    found_stat,dbpwd,prof_name,role,prof_amobile,pic = verify_login(prof_mobile, data, found_stat,dbpwd,name,role,amobile,pic)
    print("prof a mob", prof_amobile)
    print("nnn", name)
    print("db pic path", pic)

    if request.method == 'POST':
        if request.form.get('cancel'):
            print("in cancel")
            return redirect(url_for('user_dashboard'))
        button_value1 = request.form.get('save')
        button_value2 = request.form.get('upic')
        print("button_value1", button_value1)
        print("button_value2", button_value2)

        if ( button_value1 == "savedata" ):
            print("in save data")
            p_name     = request.form['p_name']
            p_mobile   = request.form['p_mobile']
            p_pmobile  = request.form['p_pmobile']
            data       = request.form
            found_stat = 'N'
            dbpwd      = " "
            name       = " "
            role       = " "
            amobile    = " "
            pic        = " "
            found_stat,dbpwd,name,role,amobile,pic = verify_login(p_mobile, data, found_stat,dbpwd,name,role,amobile,pic)
            print("found_stat:",found_stat)
            print("name:",name)
            print("role:",role)
            if ( found_stat == "Y"):    
                update_user_to_db(data)
                flash("Data Updated!", "success")
                data_audit = [formatted_date, formatted_time, session['username'], "Updated Profile"]
                create_audit(data_audit)
                session['username'] = p_name
                    # flash("Form submitted successfully!", "success")
                return redirect(url_for('update_profile'))
        if ( button_value2 == "changepic" ):
            print("in change pic")
            print(request.files)
            if 'file' not in request.files:
                flash('No file part')
                print("no file part")
                return redirect('/updateprofile')

            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                print("no file selected")
                return redirect('/updateprofile')

            if file and file.filename.endswith(('.jpg','.jpeg','.png')):
                print("in if file")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
            
                mobile = session['mobile']
                print("mobile in upload pic", mobile)
                # Optional: Preview in console
                #print(df.head())
                # Iterate and insert into DB
                upload_pic_path = filepath
                upload_pic_to_db(mobile,upload_pic_path)

                flash('Pic uploaded and data saved to database!')
                data_audit = [formatted_date, formatted_time, session['username'], "Changed Profile Pic"]
                create_audit(data_audit)
                return redirect('/updateprofile')

            else:
                flash('Invalid file type. Please upload .jpg or .jpeg or .png')
                
                return redirect('/updateprofile')
    return render_template('updateprofile.html',prof_name=prof_name,prof_mobile=prof_mobile,
                           prof_amobile=prof_amobile,username=dash_name,prof_pic=prof_pic)


@app.route("/leaderboard/")
def leader_board():
    if 'username' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login_page'))
    print("in leader board")
    now = datetime.now()
    current_year = now.year
    current_month = now.strftime('%B')
    cm=current_month
    print("current month", current_month)
    month_last1 = now - relativedelta(months=1)
    month_last2 = now - relativedelta(months=2)
    print("cur month", current_month)
    print("last ", month_last1.strftime('%B'))
    print("prev m :", month_last2.strftime('%B'))
    list1 = db_leader_board(current_month)
    print("list main page :",list1)
    name_dash = "Leader Board"
    pic = session['pic']
    print("pic:", pic)
    results   = []
    for person in list1:
        mobile = person[0]
        name   = person[1]
        marks  = person[2:]
        total = sum(marks)
        results.append((mobile, name, total, marks))
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    l1 = len(sorted_results)

    print(f"sorted res ::", sorted_results)
    print(f"sorted res len::", l1)
    
    columns = ["MNP","FWA","JioMNP","MDSSO","Sim Billing"]
    rows_jog =  [(1,2,3,4,5)]
    name1  = " "
    name2  = " "
    name3  = " "
    name4  = " "
    name5  = " "
    mob1 = " "
    mob2 = " "
    mob3 = " "
    mob4 = " "
    mob5 = ""
    pic1 = None
    pic2 = None
    pic3 = None
    pic4 = None
    pic5 = None
    res1   = " "
    res2   = " "
    res3   = " "
    res4   = " "
    res5   = " "
    i = l1
    j = l1
    if i > 0:
        mob1   = sorted_results[l1-j][0]
        name1 = sorted_results[l1-j][1]
        row1 = sorted_results[l1-j][3]
        row_name1  = (list(row1))
        res1 = [tuple(row_name1)]
        print ("res1", res1)
        data = " "
        amobile = " "
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        print("current month in leader", current_month)
        found_stat,dbpwd,prof_name,role,prof_amobile,pic1 = verify_login(mob1, data, found_stat,dbpwd,name,role,amobile,pic)
        
        #print("name1>>::", name1)
        #print("rowa ::", type(rowa))
        #print("rowa ::", rowa)
        #print("name111>>::", row_name1)
        #for row in row_name1:
        #    test.append(str(row))
        #    print("rrr", row)
        #print("tst", test)
        if (pic1):
            pic1 = "/"+pic1
        i     = i - 1
        j     = j -1
    if i > 0:
        mob2   = sorted_results[l1-j][0]
        name2 = sorted_results[l1-j][1]
        row2 = sorted_results[l1-j][3]
        row_name2  = (list(row2))
        res2 = [tuple(row_name2)]
        data = " "
        amobile = " "
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        found_stat,dbpwd,prof_name,role,prof_amobile,pic2 = verify_login(mob2, data, found_stat,dbpwd,name,role,amobile,pic)
        if (pic2):
            pic2 = "/"+pic2
        i  = i - 1
        j  = j -1
        
    if i > 0:
        mob3   = sorted_results[l1-j][0]
        name3 = sorted_results[l1-j][1]
        row3 = sorted_results[l1-j][3]
        row_name3  = (list(row3))
        res3 = [tuple(row_name3)]

        data = " "
        amobile = " "
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        found_stat,dbpwd,prof_name,role,prof_amobile,pic3 = verify_login(mob3, data, found_stat,dbpwd,name,role,amobile,pic)

        if (pic3):
            pic3 = "/"+pic3
        i  = i - 1
        j = j -1
    if i > 0:
        mob4   = sorted_results[l1-j][0]
        name4 = sorted_results[l1-j][1]
        row4 = sorted_results[l1-j][3]
        row_name4  = (list(row4))
        res4 = [tuple(row_name4)]

        data = " "
        amobile = " "
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        found_stat,dbpwd,prof_name,role,prof_amobile,pic4 = verify_login(mob4, data, found_stat,dbpwd,name,role,amobile,pic)

        if (pic4):
            pic4 = "/"+pic4
        i  = i - 1
        j = j -1
    if i > 0:
        mob5   = sorted_results[l1-j][0]
        name5 = sorted_results[l1-j][1]
        row5 = sorted_results[l1-j][3]
        row_name5  = (list(row5))
        res5 = [tuple(row_name5)]

        data = " "
        amobile = " "
        found_stat = 'N'
        dbpwd = " "
        name = " "
        role = " "
        found_stat,dbpwd,prof_name,role,prof_amobile,pic5 = verify_login(mob5, data, found_stat,dbpwd,name,role,amobile,pic)
        if (pic5):
            pic5 = "/"+pic5
        i  = i - 1
        j = j -1

    #print(f"n2 ::", sorted_results[4][0])
    pic = session['pic']
    print("pic bef leader #####:", pic)
    print("pic1 bef leader #####:", pic1)
    print("pic2 bef leader #####:", pic2)
    print("pic3 bef leader #####:", pic3)
    print("pic4 bef leader #####:", pic4)
    print("pic5 bef leader #####:", pic5)
    return render_template('leaderboard.html',columns=columns,username=name_dash,name1=name1,name2=name2,name3=name3,row1=res1,row2=res2,row3=res3,row4=res4,row5=res5,prof_pic=pic,pic1=pic1,pic2=pic2,pic3=pic3,pic4=pic4,pic5=pic5,cm=current_month)

print(__name__)
if __name__ == "__main__":
    app.config['SQLALCHEMY_DATABASE_URI'] =  "mysql+pymysql://4SzmE32uEz5t8DV.root:LCwy8CL3iWqMpxRD@gateway01.ap-southeast-1.prod.aws.tidbcloud.com/test?charset=utf8mb4"
    print("I am in if")
    app.run(host ='0.0.0.0',port=8080, debug=True)
    