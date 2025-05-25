from flask import Flask, jsonify, request
#from flaskext.mysql import MySQL
import mysql.connector.pooling
from datetime import datetime
import pytz
import openpyxl 
import asyncio


# mysql = MySQL()

app = Flask(__name__)

# app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1';
# app.config['MYSQL_DATABASE_PORT'] = 3307;
# app.config['MYSQL_DATABASE_USER'] = 'isara';
# app.config['MYSQL_DATABASE_PASSWORD'] = '1234';
# app.config['MYSQL_DATABASE_DB'] = 'mydb';
# mysql.init_app(app)
# cursor = mysql.get_db().cursor()

# my_database = MySQL(app, prefix="my_database", host="localhost", user="isara", password="1234", db="mydb", port=8888,autocommit=True)
# connection = my_database.connect()
# cursor = connection.cursor()



connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    user="isara",
    password="1234",
    host="localhost",
    port=3307,  #3306
    database="tsubakimoto" #akt1
)

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

@app.route('/test_db', methods=['GET'])
def get_test_db():
    app.logger.info('/test_db')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('select * from exchange_rate')
    data = cursor.fetchall()
    cursor.close()
    conn.close() 
    return jsonify(data)

@app.route('/master_data/upload', methods=['POST'])
async def get_masterdata_upload():
    app.logger.info('/master_data/upload')
    
    #request mysql connection from pool
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    
    # upload file
    file = request.files['file']
    fullfilename = file.filename
    onlyfilename = fullfilename.split('.')[0];
    onlyfilename = onlyfilename.replace(' ','_')
    onlyfilename = onlyfilename.replace('-','_')
    onlyfileext = fullfilename.split('.')[1];
    print(request.files);
    newpath = "uploaded_files/" + onlyfilename  + "_" + datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%Y_%m_%d_%H_%M_%S') + "." + onlyfileext;
    app.logger.info("uploaded new file path : "+newpath)
    file.save(newpath)
    
    # parse file
    wb = openpyxl.load_workbook(newpath,data_only=True)
    ws = wb.active
    print('Total number of rows: '+str(ws.max_row)+'. And total number of columns: '+str(ws.max_column))
    for row in range(5, ws.max_row+1):
        sql="insert into master_tsubakimoto(category,part_no,previous_model_no,new_model_no,unit,manufacturer_suggested_retail_price,new_manufacturer_suggested_retail_price,conversion_to_ft,diff_for_cost,op_price,po_price_jpy_usd,po_price_currency,remark,thb_cost,gp,pricelist_name,multiplier,make_same_price_as_standard_price,new_make_same_price_as_standard_price,standard_price,diff,dist_pl_mull,dist_ex_rate,unit_price,new_unit_price,diff_unit_price,status,supplier_name,stock_reference,cutting_assembly,detail)";
        sql += " values (";
        for column in range(1, ws.max_column+1):
            val = ws.cell(row,column).value
            if val is str:
                val = val.replace('\n','')
                val = val.replace('\r','')
                val = val.replace('\t','')
            elif val is None or val == '#VALUE!':
                val = "";
            if column < ws.max_column:
                sql += "'"
                sql += str(val);
                sql += "',"
                if val == "":
                    print("", end=",")
                else:
                    print(val, end=",")
            else:
                sql += "'"
                sql += str(val)
                sql += "')"
                if val == "":
                    print("", end="")
                else:
                    print(val, end="")
        print()
        
        #print sql for reviewing
        print("sql="+sql);
        
        #run sql
        cursor.execute(sql)
        
        print()
        print()
    
    
    
    data = { 
        "status":"true",
        "upload_excel":
        {
        "result": "pass",
        "full uploaded file path": newpath
        }
        } 
    
    #commit changes to databse
    conn.commit()
    
    #return mysql connection to pool
    cursor.close()
    conn.close() 
    
    await asyncio.sleep(5)
    
    #return json response
    return jsonify(data)

@app.route('/master_data/listall', methods=['POST'])
def get_masterdata_listall():
    app.logger.info('/master_data/listall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('select * from master_tsubakimoto')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/master_formula/upload', methods=['POST'])
async def get_masterformula_upload():
    app.logger.info('/master_formula/upload')

    #request mysql connection from pool
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    # upload file
    file = request.files['file']
    fullfilename = file.filename
    onlyfilename = fullfilename.split('.')[0];
    onlyfilename = onlyfilename.replace(' ','_')
    onlyfilename = onlyfilename.replace('-','_')
    onlyfileext = fullfilename.split('.')[1];
    print(request.files);
    newpath = "uploaded_files/" + onlyfilename  + "_" + datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%Y_%m_%d_%H_%M_%S') + "." + onlyfileext;
    app.logger.info("uploaded new file path : "+newpath)
    file.save(newpath)

    # parse file
    wb = openpyxl.load_workbook(newpath,data_only=False)
    ws = wb.active
    print('Total number of rows: '+str(ws.max_row)+'. And total number of columns: '+str(ws.max_column))
    for row in range(5, ws.max_row+1):
        sql="insert into master_tsubakimoto_formula(category,part_no,previous_model_no,new_model_no,unit,manufacturer_suggested_retail_price,new_manufacturer_suggested_retail_price,conversion_to_ft,diff_for_cost,op_price,po_price_jpy_usd,po_price_currency,remark,thb_cost,gp,pricelist_name,multiplier,make_same_price_as_standard_price,new_make_same_price_as_standard_price,standard_price,diff,dist_pl_mull,dist_ex_rate,unit_price,new_unit_price,diff_unit_price,status,supplier_name,stock_reference,cutting_assembly,detail)";
        sql += " values (";
        for column in range(1, ws.max_column+1):
            val = ws.cell(row,column).value
            if val is str:
                val = val.replace('\n','')
                val = val.replace('\r','')
                val = val.replace('\t','')
            elif val is None or val == '#VALUE!':
                val = "";
            if column < ws.max_column:
                sql += "'"
                sql += str(val);
                sql += "',"
                if val == "":
                    print("", end=",")
                else:
                    print(val, end=",")
            else:
                sql += "'"
                sql += str(val)
                sql += "')"
                if val == "":
                    print("", end="")
                else:
                    print(val, end="")
        print()

        #print sql for reviewing
        print("sql="+sql);

        #run sql
        cursor.execute(sql)

        print()
        print()



    data = {
        "status":"true",
        "upload_excel":
        {
        "result": "pass",
        "full uploaded file path": newpath
        }
        }

    #commit changes to databse
    conn.commit()

    #return mysql connection to pool
    cursor.close()
    conn.close()

    await asyncio.sleep(5)

    #return json response
    return jsonify(data)

@app.route('/master_formula/listall', methods=['POST'])
def get_masterformula_listall():
    app.logger.info('/master_formula/listall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('select * from master_tsubakimoto_formula')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/exchange_rate/upload', methods=['POST'])
async def get_exchangerate_upload():
    app.logger.info('/master_formula/upload')

    #request mysql connection from pool
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    # upload file
    file = request.files['file']
    fullfilename = file.filename
    onlyfilename = fullfilename.split('.')[0];
    onlyfilename = onlyfilename.replace(' ','_')
    onlyfilename = onlyfilename.replace('-','_')
    onlyfileext = fullfilename.split('.')[1];
    print(request.files);
    newpath = "uploaded_files/" + onlyfilename  + "_" + datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%Y_%m_%d_%H_%M_%S') + "." + onlyfileext;
    app.logger.info("uploaded new file path : "+newpath)
    file.save(newpath)

    # parse file
    wb = openpyxl.load_workbook(newpath,data_only=True)
    ws = wb.active
    print('Total number of rows: '+str(ws.max_row)+'. And total number of columns: '+str(ws.max_column))

    usd_br = ws.cell(2,2).value
    print('usd_br='+str(usd_br))
    eur_br = ws.cell(2,3).value
    print('eur_br='+str(eur_br))
    jpy_br = ws.cell(2,4).value
    print('jpy_br='+str(jpy_br))

    usd_cr = ws.cell(3,2).value
    print('usd_cr='+str(usd_cr))
    eur_cr = ws.cell(3,3).value
    print('eur_cr='+str(eur_cr))
    jpy_cr = ws.cell(3,4).value
    print('jpy_cr='+str(jpy_cr))

    usd_pr = ws.cell(4,2).value
    print('usd_pr='+str(usd_pr))
    eur_pr = ws.cell(4,3).value
    print('eur_pr='+str(eur_pr))
    jpy_pr = ws.cell(4,4).value
    print('jpy_pr='+str(jpy_pr))

    usd_qr = ws.cell(5,2).value
    print('usd_qr='+str(usd_qr))
    eur_qr = ws.cell(5,3).value
    print('eur_qr='+str(eur_qr))
    jpy_qr = ws.cell(5,4).value
    print('jpy_qr='+str(jpy_qr))

    remark = ws.cell(6,2).value

    sql="insert into exchange_rate(usd_br,usd_cr,usd_pr,usd_qr,eur_br,eur_cr,eur_qr,eur_pr,jpy_br,jpy_cr,jpy_pr,jpy_qr,rate_remark,rate_file_name,rate_path)"
    sql += " values ("
    sql += str(usd_br)
    sql += ","
    sql += str(usd_cr)
    sql += ","
    sql += str(usd_pr)
    sql += ","
    sql += str(usd_qr)
    sql += ","
    sql += str(eur_br)
    sql += ","
    sql += str(eur_cr)
    sql += ","
    sql += str(eur_pr)
    sql += ","
    sql += str(eur_qr)
    sql += ","
    sql += str(jpy_br)
    sql += ","
    sql += str(jpy_cr)
    sql += ","
    sql += str(jpy_pr)
    sql += ","
    sql += str(jpy_qr)
    sql += ",'"
    sql += remark
    sql += "','"
    sql += onlyfilename
    sql += "','"
    sql += newpath
    sql += "')"

    #print sql for reviewing
    print("sql="+sql);

    #run sql
    cursor.execute(sql)

    print()
    print()


    data = {
        "status":"true",
        "upload_excel":
        {
        "result": "pass",
        "full uploaded file path": newpath
        }
        }

    #commit changes to databse
    conn.commit()

    #return mysql connection to pool
    cursor.close()
    conn.close()

    await asyncio.sleep(5)

    #return json response
    return jsonify(data)

@app.route('/exchange_rate/listall', methods=['POST'])
def get_exchangerate_listall():
    app.logger.info('/exchange_rate/listall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('select * from exchange_rate')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# In-memory data store
# items = [{"id": 1, "name": "This is item 1"}, {"id": 2, "name": "This is item 2"}]

# GET request: Retrieve all items
# @app.route('/api/items', methods=['GET'])
# def get_items():
#     return jsonify(items)

# GET request: Retrieve a specific item by ID
# @app.route('/api/items/<int:item_id>', methods=['GET'])
# def get_item(item_id):
#     item = next((item for item in items if item["id"] == item_id), None)
#     if item is None:
#         return jsonify({"error": "Item not found"}), 404
#     return jsonify(item)

# POST request: Create a new item
# @app.route('/api/items', methods=['POST'])
# def create_item():
#     new_item = {"id": len(items) + 1, "name": request.json.get('name')}
#     items.append(new_item)
#     return jsonify(new_item), 201



if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0',debug=True)
