import sqlalchemy
from sqlalchemy import create_engine, text
print(sqlalchemy.__version__)

db_connection_string =  "mysql+pymysql://4SzmE32uEz5t8DV.root:LCwy8CL3iWqMpxRD@gateway01.ap-southeast-1.prod.aws.tidbcloud.com/test?charset=utf8mb4"

engine = create_engine(db_connection_string,connect_args={
    "ssl" :{
        "ca": "/etc/ssl/cert.pem"
    }
})

with engine.connect() as conn:
    query = "SELECT * from users"
    result = conn.execute(text(query))

result_all = result.mappings().all()
result_dict = []
for row in result_all:
    result_dict.append(dict(row))
print(result_dict)
print(type(result_dict))

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


  




