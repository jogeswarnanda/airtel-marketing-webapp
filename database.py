import sqlalchemy
from sqlalchemy import create_engine, text
import os
import certifi
import ssl
import urllib.request
from dotenv import load_dotenv
load_dotenv()
#print(sqlalchemy.__version__)

db_connection_string =  os.getenv('DB_CONNECTION_STRING')
#print("conn str" , db_connection_string)
db_s_string =  os.getenv('DB_SIKAN')
#print("conn str sk" , db_s_string)

engine = create_engine(db_connection_string,connect_args={
    "ssl" :{
        "ca": "certs/cert.pem"
    }
})

with engine.connect() as conn:
    query  = "SELECT * from users"
    result = conn.execute(text(query))

result_all  = result.mappings().all()
result_dict = []
for row in result_all:
    result_dict.append(dict(row))
print(result_dict)
print(type(result_dict))

def verify_login (signup_mobile,data,found_stat,dbpwd,name,role,amobile,pic):
  print("mobile no. entered by user:", signup_mobile)
  dbpwd      = " "
  name       = " "
  role       = " "
  amobile    = " "
  pic        = " "
  found_stat = " "
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users where user_mobile = :usermobile"),
           {"usermobile" : signup_mobile});
    rows = result.all()
    print(type(rows))
    print("rows_new@@::", rows)
    #print(rows[0][4])
    if len(rows) == 0:
      found_stat = "N"
      #print("set found sta N:")
      return found_stat,dbpwd,name,role,amobile,pic
    else:
      print("set found stat YY")
      found_stat = "Y"
      dbpwd      = rows[0][2]
      name       = rows[0][1]
      role       = rows[0][3]
      amobile    = rows[0][4]
      pic        = rows[0][5]
      #print("pwd", dbpwd)
      return found_stat,dbpwd,name,role,amobile,pic

def add_user_to_db(data):
  with engine.connect() as conn:
    result1 = conn.execute(text("INSERT INTO users (user_mobile,user_name,user_password,user_role,user_alt_number) VALUES(:u_mobile,:u_name,:u_password,:u_role,:u_alt_number)"),
    {"u_mobile": data.get("s_mobile"), "u_name" : data.get("s_name"),"u_password" : data.get("s_password"),"u_role" : data.get("s_role",),"u_alt_number" : data.get("s_alt_number")});
    conn.commit()

def fetch_upload_data (s_mobile):
  print('IN user table')
  f_mobile = s_mobile
  list_all= []
  with engine.connect() as conn:
    result   = conn.execute(text("SELECT * FROM user_uploads where upload_mobile = :f_mobile"), {"f_mobile" : f_mobile});
    columns  = ["Month","MNP","FWA","JioMNP","MDSSO","Sim Billing"]
    rows_all = result.fetchall()
    #print("rows_all", rows_all)
    for row in rows_all:
      rows_s = (row.upload_month,row.upload_mnp,row.upload_fwa,row.upload_jmnp,row.upload_mdsso,row.upload_simbilling)
      list_all.append(rows_s)
  print("list_all", list_all)
  return columns,list_all

def upload_data(upload):
  uploadid = upload.upload_id
  #print("upload db", upload)
  #print("upload db", upload.upload_id)
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM user_uploads where upload_id = :uploadid1"),
           {"uploadid1" : uploadid});
    rows = result.all()
    if len(rows) == 0:
      result1 = conn.execute(text("INSERT INTO user_uploads (upload_id,upload_mobile,upload_name,upload_month,upload_role,upload_fwa,upload_jmnp,upload_mnp,upload_mdsso,upload_simbilling) VALUES(:u_id,:u_mobile,:u_name,:u_month,:u_role,:u_fwa,:u_jmnp,:u_mnp,:u_mdsso,:u_simbilling)"),
      {"u_id": upload.upload_id, "u_mobile" : upload.upload_mobile,"u_name" : upload.upload_name,"u_month" : upload.upload_month,"u_role" : upload.upload_role,"u_fwa" : upload.upload_fwa,"u_jmnp" : upload.upload_jmnp,"u_mnp" : upload.upload_mnp,"u_mdsso" : upload.upload_mdsso,"u_simbilling" : upload.upload_simbilling});
      conn.commit()
    else:
      #print("update ", upload.upload_id)
      #print("update ", upload.upload_mnp)
      result1 = conn.execute(text("""
      UPDATE user_uploads
      SET
        upload_mobile = :u_mobile,
        upload_name = :u_name,
        upload_month = :u_month,
        upload_role = :u_role,
        upload_fwa = :u_fwa,
        upload_jmnp = :u_jmnp,
        upload_mnp = :u_mnp,
        upload_mdsso = :u_mdsso,
        upload_simbilling = :u_simbilling
        WHERE upload_id = :u_id
        """),
      {
        "u_id": upload.upload_id,
        "u_mobile": upload.upload_mobile,
        "u_name": upload.upload_name,
        "u_month": upload.upload_month,
        "u_role": upload.upload_role,
        "u_fwa": upload.upload_fwa,
        "u_jmnp": upload.upload_jmnp,
        "u_mnp": upload.upload_mnp,
        "u_mdsso": upload.upload_mdsso,
        "u_simbilling": upload.upload_simbilling
      })
      conn.commit()

def update_user_to_db(data):
  #print("in update profile db", data)
  with engine.connect() as conn:
    result1 = conn.execute(text("""
      UPDATE users
      SET
        user_name = :p_name,
        user_alt_number = :p_pmobile      
        WHERE user_mobile = :p_mobile                                          
        """),
      {
        "p_name": data.get("p_name"),
        "p_mobile": data.get("p_mobile"),
        "p_pmobile": data.get("p_pmobile")
      })
    conn.commit()

#def admin_update(mobile):
##  with engine.connect() as conn:
 #   cursor = conn.cursor()
 ##   cursor.execute("""
  #  UPDATE users SET name = %s, email = %s, user_mobile = %s WHERE id = %s
  #  """, (name, email, mobile, user_id))
 # mysql.connection.commit()
 # cursor.close()
  
  #print("in update profile db", data)
  #with engine.connect() as conn:
   # result1 = conn.execute(text("""
    #  UPDATE users
     # SET
     #   user_name = :p_name,
      #  user_alt_number = :p_pmobile      
      #  WHERE user_mobile = :p_mobile                                          
      #  """),
     # {
     #   "p_name": data.get("p_name"),
     #   "p_mobile": data.get("p_mobile"),
     #   "p_pmobile": data.get("p_pmobile")
     # })
    #conn.commit()

def upload_pic_to_db(mobile,filepath):
  with engine.begin() as conn:  # engine.begin() handles commit automatically
        conn.execute(
            text("""
                UPDATE users
                SET user_profile_pic = :p_path
                WHERE user_mobile = :p_mobile
            """),
            {
                "p_mobile": mobile,
                "p_path": filepath
            }
        )
        conn.commit()

def db_leader_board(month):
  print("in db_leader_board", month)
  with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM user_uploads where upload_month = :u_month"), {"u_month" : month});
    columns = ["Month","MNP","FWA","JioMNP","MDSSO","Sim Billing"]
    rows_all = result.fetchall()
    print("rows_all", rows_all)
    curr_month_list = []
    for row in rows_all:
      rows_s = (row.upload_mobile,row.upload_name,row.upload_mnp,row.upload_fwa,row.upload_jmnp,row.upload_mdsso,row.upload_simbilling)
      print("rows_s", rows_s)
      curr_month_list.append(rows_s)
  
  return curr_month_list

#result_dict1 = dict()
#result_dict1 = dict(result_dict.key)
#print(type(result_dict1))
#print(result_dict1)
#first_r = result_all[0]
#first_d = (dict(first_r))
#print(type(first_d))
#print(first_d)
#result_dict = list()
#for row in result.all():
#    print(row)
#    result_dict.append(row)
#print(type(result_dict))


  




