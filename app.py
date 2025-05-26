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

@app.route('/master_data/deleteall', methods=['POST'])
def get_masterdata_deleteall():
    app.logger.info('/master_data/deleteall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('delete from master_tsubakimoto')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    data = {
        "status":"true",
        "delete all masterdata":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_data/update', methods=['POST'])
def get_masterdata_update():
    app.logger.info('/master_data/update')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "update master_tsubakimoto set "

    if request.form.get('category') is not None:
        sql += ","
        sql += "category='"
        sql += request.form.get('category')
        sql += "'"

    if request.form.get('part_no') is not None:
        sql += ","
        sql += "part_no='"
        sql += request.form.get('part_no')
        sql += "'"

    if request.form.get('previous_model_no') is not None:
        sql += ","
        sql += "previous_model_no='"
        sql += request.form.get('previous_model_no')
        sql += "'"

    if request.form.get('new_model_no') is not None:
        sql += ","
        sql += "new_model_no='"
        sql += request.form.get('new_model_no')
        sql += "'"

    if request.form.get('new_model_no') is not None:
        sql += ","
        sql += "unit='"
        sql += request.form.get('new_model_no')
        sql += "'"

    if request.form.get('manufacturer_suggested_retail_price') is not None:
        sql += ","
        sql += "manufacturer_suggested_retail_price='"
        sql += request.form.get('manufacturer_suggested_retail_price')
        sql += "'"

    if request.form.get('new_manufacturer_suggested_retail_price') is not None:
        sql += ","
        sql += "new_manufacturer_suggested_retail_price='"
        sql += request.form.get('new_manufacturer_suggested_retail_price')
        sql += "'"

    if request.form.get('conversion_to_ft') is not None:
        sql += ","
        sql += "conversion_to_ft='"
        sql += request.form.get('conversion_to_ft')
        sql += "'"

    if request.form.get('diff_for_cost') is not None:
        sql += ","
        sql += "diff_for_cost='"
        sql += request.form.get('diff_for_cost')
        sql += "'"

    if request.form.get('op_price') is not None:
        sql += ","
        sql += "op_price='"
        sql += request.form.get('op_price')
        sql += "'"

    if request.form.get('po_price_jpy_usd') is not None:
        sql += ","
        sql += "po_price_jpy_usd='"
        sql += request.form.get('po_price_jpy_usd')
        sql += "'"

    if request.form.get('po_price_currency') is not None:
        sql += ","
        sql += "po_price_currency='"
        sql += request.form.get('po_price_currency')
        sql += "'"

    if request.form.get('remark') is not None:
        sql += ","
        sql += "remark='"
        sql += request.form.get('remark')
        sql += "'"

    if request.form.get('thb_cost') is not None:
        sql += ","
        sql += "thb_cost='"
        sql += request.form.get('thb_cost')
        sql += "'"

    if request.form.get('gp') is not None:
        sql += ","
        sql += "gp='"
        sql += request.form.get('gp')
        sql += "'"

    if request.form.get('pricelist_name') is not None:
        sql += ","
        sql += "pricelist_name='"
        sql += request.form.get('pricelist_name')
        sql += "'"

    if request.form.get('multiplier') is not None:
        sql += ","
        sql += "multiplier='"
        sql += request.form.get('multiplier')
        sql += "'"

    if request.form.get('make_same_price_as_standard_price') is not None:
        sql += ","
        sql += "make_same_price_as_standard_price='"
        sql += request.form.get('make_same_price_as_standard_price')
        sql += "'"

    if request.form.get('new_make_same_price_as_standard_price') is not None:
        sql += ","
        sql += "new_make_same_price_as_standard_price='"
        sql += request.form.get('new_make_same_price_as_standard_price')
        sql += "'"

    if request.form.get('standard_price') is not None:
        sql += ","
        sql += "standard_price='"
        sql += request.form.get('standard_price')
        sql += "'"

    if request.form.get('diff') is not None:
        sql += ","
        sql += "diff='"
        sql += request.form.get('diff')
        sql += "'"

    if request.form.get('dist_pl_mul') is not None:
        sql += ","
        sql += "dist_pl_mull='"
        sql += request.form.get('dist_pl_mul')
        sql += "'"

    if request.form.get('dist_ex_rate') is not None:
        sql += ","
        sql += "dist_ex_rate='"
        sql += request.form.get('dist_ex_rate')
        sql += "'"

    if request.form.get('unit_price') is not None:
        sql += ","
        sql += "unit_price='"
        sql += request.form.get('unit_price')
        sql += "'"

    if request.form.get('new_unit_price') is not None:
        sql += ","
        sql += "new_unit_price='"
        sql += request.form.get('new_unit_price')
        sql += "'"

    if request.form.get('diff_unit_price') is not None:
        sql += ","
        sql += "diff_unit_price='"
        sql += request.form.get('diff_unit_price')
        sql += "'"

    if request.form.get('status') is not None:
        sql += ","
        sql += "status='"
        sql += request.form.get('status')
        sql += "'"

    if request.form.get('supplier_name') is not None:
        sql += ","
        sql += "supplier_name='"
        sql += request.form.get('supplier_name')
        sql += "'"

    if request.form.get('stock_reference') is not None:
        sql += ","
        sql += "stock_reference='"
        sql += request.form.get('stock_reference')
        sql += "'"

    if request.form.get('cutting_assembly') is not None:
        sql += ","
        sql += "cutting_assembly='"
        sql += request.form.get('cutting_assembly')
        sql += "'"

    if request.form.get('detail') is not None:
        sql += ","
        sql += "detail='"
        sql += request.form.get('detail')
        sql += "'"

    sql += " where Id="
    sql += request.form.get('Id')

    sql = sql.replace('update master_tsubakimoto set ,','update master_tsubakimoto set ')
    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "update masterdata":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_data/add', methods=['POST'])
def get_masterdata_add():
    app.logger.info('/master_data/update')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "insert into master_tsubakimoto";
    sql += "(category,";
    sql += "part_no,";
    sql += "previous_model_no,";
    sql += "new_model_no,";
    sql += "unit,";
    sql += "manufacturer_suggested_retail_price,";
    sql += "new_manufacturer_suggested_retail_price,";
    sql += "conversion_to_ft,";
    sql += "diff_for_cost,";
    sql += "op_price,";
    sql += "po_price_jpy_usd,";
    sql += "po_price_currency,";
    sql += "remark,";
    sql += "thb_cost,";
    sql += "gp,";
    sql += "pricelist_name,";
    sql += "multiplier,";
    sql += "make_same_price_as_standard_price,";
    sql += "new_make_same_price_as_standard_price,";
    sql += "standard_price,";
    sql += "diff,";
    sql += "dist_pl_mull,";
    sql += "dist_ex_rate,";
    sql += "unit_price,";
    sql += "new_unit_price,";
    sql += "diff_unit_price,";
    sql += "status,";
    sql += "supplier_name,";
    sql += "stock_reference,";
    sql += "cutting_assembly,";
    sql += "detail)";
    sql += " values (";

    sql += "'"
    if request.form.get('category') is not None:
        sql += request.form.get('category')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('part_no') is not None:
     sql += request.form.get('part_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('previous_model_no') is not None:
        sql += request.form.get('previous_model_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_model_no') is not None:
        sql += request.form.get('new_model_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('unit') is not None:
        sql += request.form.get('unit')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('manufacturer_suggested_retail_price') is not None:
        sql += request.form.get('manufacturer_suggested_retail_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_manufacturer_suggested_retail_price') is not None:
        sql += request.form.get('new_manufacturer_suggested_retail_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('conversion_to_ft') is not None:
        sql += request.form.get('conversion_to_ft')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff_for_cost') is not None:
        sql += request.form.get('diff_for_cost')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('op_price') is not None:
        sql += request.form.get('op_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('po_price_jpy_usd') is not None:
        sql += request.form.get('po_price_jpy_usd')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('po_price_currency') is not None:
        sql += request.form.get('po_price_currency')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('remark') is not None:
        sql += request.form.get('remark')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('thb_cost') is not None:
        sql += request.form.get('thb_cost')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('gp') is not None:
        sql += request.form.get('gp')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('pricelist_name') is not None:
        sql += request.form.get('pricelist_name')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('multiplier') is not None:
     sql += request.form.get('multiplier')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('make_same_price_as_standard_price') is not None:
        sql += request.form.get('make_same_price_as_standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_make_same_price_as_standard_price') is not None:
        sql += request.form.get('new_make_same_price_as_standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('standard_price') is not None:
        sql += request.form.get('standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff') is not None:
        sql += request.form.get('diff')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('dist_pl_mull') is not None:
        sql += request.form.get('dist_pl_mull')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('dist_ex_rate') is not None:
        sql += request.form.get('dist_ex_rate')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('unit_price') is not None:
        sql += request.form.get('unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_unit_price') is not None:
        sql += request.form.get('new_unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff_unit_price') is not None:
        sql += request.form.get('diff_unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('status') is not None:
        sql += request.form.get('status')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('supplier_name') is not None:
        sql += request.form.get('supplier_name')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('stock_reference') is not None:
        sql += request.form.get('stock_reference')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('cutting_assembly') is not None:
        sql += request.form.get('cutting_assembly')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('detail') is not None:
        sql += request.form.get('detail')
    sql += "'"

    sql += ")";

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "add masterdata":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_data/delete', methods=['POST'])
def get_masterdata_delete():
    app.logger.info('/master_data/delete')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "delete from master_tsubakimoto"
    sql += " where Id="
    sql += request.form.get('Id')

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "delete masterdata with id":
            {
                "result": "pass"
            }
    }
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

@app.route('/master_formula/deleteall', methods=['POST'])
def get_masterformula_deleteall():
    app.logger.info('/master_data/deleteall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('delete from master_tsubakimoto_formula')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    data = {
        "status":"true",
        "delete all masterdata formula":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_formula/update', methods=['POST'])
def get_masterformula_update():
    app.logger.info('/master_data/update')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "update master_tsubakimoto_formula set "

    if request.form.get('category') is not None:
        sql += ","
        sql += "category='"
        sql += request.form.get('category')
        sql += "'"

    if request.form.get('part_no') is not None:
        sql += ","
        sql += "part_no='"
        sql += request.form.get('part_no')
        sql += "'"

    if request.form.get('previous_model_no') is not None:
        sql += ","
        sql += "previous_model_no='"
        sql += request.form.get('previous_model_no')
        sql += "'"

    if request.form.get('new_model_no') is not None:
        sql += ","
        sql += "new_model_no='"
        sql += request.form.get('new_model_no')
        sql += "'"

    if request.form.get('new_model_no') is not None:
        sql += ","
        sql += "unit='"
        sql += request.form.get('new_model_no')
        sql += "'"

    if request.form.get('manufacturer_suggested_retail_price') is not None:
        sql += ","
        sql += "manufacturer_suggested_retail_price='"
        sql += request.form.get('manufacturer_suggested_retail_price')
        sql += "'"

    if request.form.get('new_manufacturer_suggested_retail_price') is not None:
        sql += ","
        sql += "new_manufacturer_suggested_retail_price='"
        sql += request.form.get('new_manufacturer_suggested_retail_price')
        sql += "'"

    if request.form.get('conversion_to_ft') is not None:
        sql += ","
        sql += "conversion_to_ft='"
        sql += request.form.get('conversion_to_ft')
        sql += "'"

    if request.form.get('diff_for_cost') is not None:
        sql += ","
        sql += "diff_for_cost='"
        sql += request.form.get('diff_for_cost')
        sql += "'"

    if request.form.get('op_price') is not None:
        sql += ","
        sql += "op_price='"
        sql += request.form.get('op_price')
        sql += "'"

    if request.form.get('po_price_jpy_usd') is not None:
        sql += ","
        sql += "po_price_jpy_usd='"
        sql += request.form.get('po_price_jpy_usd')
        sql += "'"

    if request.form.get('po_price_currency') is not None:
        sql += ","
        sql += "po_price_currency='"
        sql += request.form.get('po_price_currency')
        sql += "'"

    if request.form.get('remark') is not None:
        sql += ","
        sql += "remark='"
        sql += request.form.get('remark')
        sql += "'"

    if request.form.get('thb_cost') is not None:
        sql += ","
        sql += "thb_cost='"
        sql += request.form.get('thb_cost')
        sql += "'"

    if request.form.get('gp') is not None:
        sql += ","
        sql += "gp='"
        sql += request.form.get('gp')
        sql += "'"

    if request.form.get('pricelist_name') is not None:
        sql += ","
        sql += "pricelist_name='"
        sql += request.form.get('pricelist_name')
        sql += "'"

    if request.form.get('multiplier') is not None:
        sql += ","
        sql += "multiplier='"
        sql += request.form.get('multiplier')
        sql += "'"

    if request.form.get('make_same_price_as_standard_price') is not None:
        sql += ","
        sql += "make_same_price_as_standard_price='"
        sql += request.form.get('make_same_price_as_standard_price')
        sql += "'"

    if request.form.get('new_make_same_price_as_standard_price') is not None:
        sql += ","
        sql += "new_make_same_price_as_standard_price='"
        sql += request.form.get('new_make_same_price_as_standard_price')
        sql += "'"

    if request.form.get('standard_price') is not None:
        sql += ","
        sql += "standard_price='"
        sql += request.form.get('standard_price')
        sql += "'"

    if request.form.get('diff') is not None:
        sql += ","
        sql += "diff='"
        sql += request.form.get('diff')
        sql += "'"

    if request.form.get('dist_pl_mul') is not None:
        sql += ","
        sql += "dist_pl_mull='"
        sql += request.form.get('dist_pl_mul')
        sql += "'"

    if request.form.get('dist_ex_rate') is not None:
        sql += ","
        sql += "dist_ex_rate='"
        sql += request.form.get('dist_ex_rate')
        sql += "'"

    if request.form.get('unit_price') is not None:
        sql += ","
        sql += "unit_price='"
        sql += request.form.get('unit_price')
        sql += "'"

    if request.form.get('new_unit_price') is not None:
        sql += ","
        sql += "new_unit_price='"
        sql += request.form.get('new_unit_price')
        sql += "'"

    if request.form.get('diff_unit_price') is not None:
        sql += ","
        sql += "diff_unit_price='"
        sql += request.form.get('diff_unit_price')
        sql += "'"

    if request.form.get('status') is not None:
        sql += ","
        sql += "status='"
        sql += request.form.get('status')
        sql += "'"

    if request.form.get('supplier_name') is not None:
        sql += ","
        sql += "supplier_name='"
        sql += request.form.get('supplier_name')
        sql += "'"

    if request.form.get('stock_reference') is not None:
        sql += ","
        sql += "stock_reference='"
        sql += request.form.get('stock_reference')
        sql += "'"

    if request.form.get('cutting_assembly') is not None:
        sql += ","
        sql += "cutting_assembly='"
        sql += request.form.get('cutting_assembly')
        sql += "'"

    if request.form.get('detail') is not None:
        sql += ","
        sql += "detail='"
        sql += request.form.get('detail')
        sql += "'"

    sql += " where Id="
    sql += request.form.get('Id')

    sql = sql.replace('update master_tsubakimoto set ,','update master_tsubakimoto set ')
    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "update masterdata":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_formula/add', methods=['POST'])
def get_masterformula_add():
    app.logger.info('/master_data/update')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "insert into master_tsubakimoto_formula";
    sql += "(category,";
    sql += "part_no,";
    sql += "previous_model_no,";
    sql += "new_model_no,";
    sql += "unit,";
    sql += "manufacturer_suggested_retail_price,";
    sql += "new_manufacturer_suggested_retail_price,";
    sql += "conversion_to_ft,";
    sql += "diff_for_cost,";
    sql += "op_price,";
    sql += "po_price_jpy_usd,";
    sql += "po_price_currency,";
    sql += "remark,";
    sql += "thb_cost,";
    sql += "gp,";
    sql += "pricelist_name,";
    sql += "multiplier,";
    sql += "make_same_price_as_standard_price,";
    sql += "new_make_same_price_as_standard_price,";
    sql += "standard_price,";
    sql += "diff,";
    sql += "dist_pl_mull,";
    sql += "dist_ex_rate,";
    sql += "unit_price,";
    sql += "new_unit_price,";
    sql += "diff_unit_price,";
    sql += "status,";
    sql += "supplier_name,";
    sql += "stock_reference,";
    sql += "cutting_assembly,";
    sql += "detail)";
    sql += " values (";

    sql += "'"
    if request.form.get('category') is not None:
        sql += request.form.get('category')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('part_no') is not None:
        sql += request.form.get('part_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('previous_model_no') is not None:
        sql += request.form.get('previous_model_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_model_no') is not None:
        sql += request.form.get('new_model_no')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('unit') is not None:
        sql += request.form.get('unit')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('manufacturer_suggested_retail_price') is not None:
        sql += request.form.get('manufacturer_suggested_retail_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_manufacturer_suggested_retail_price') is not None:
        sql += request.form.get('new_manufacturer_suggested_retail_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('conversion_to_ft') is not None:
        sql += request.form.get('conversion_to_ft')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff_for_cost') is not None:
        sql += request.form.get('diff_for_cost')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('op_price') is not None:
        sql += request.form.get('op_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('po_price_jpy_usd') is not None:
        sql += request.form.get('po_price_jpy_usd')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('po_price_currency') is not None:
        sql += request.form.get('po_price_currency')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('remark') is not None:
        sql += request.form.get('remark')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('thb_cost') is not None:
        sql += request.form.get('thb_cost')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('gp') is not None:
        sql += request.form.get('gp')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('pricelist_name') is not None:
        sql += request.form.get('pricelist_name')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('multiplier') is not None:
        sql += request.form.get('multiplier')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('make_same_price_as_standard_price') is not None:
        sql += request.form.get('make_same_price_as_standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_make_same_price_as_standard_price') is not None:
        sql += request.form.get('new_make_same_price_as_standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('standard_price') is not None:
        sql += request.form.get('standard_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff') is not None:
        sql += request.form.get('diff')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('dist_pl_mull') is not None:
        sql += request.form.get('dist_pl_mull')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('dist_ex_rate') is not None:
        sql += request.form.get('dist_ex_rate')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('unit_price') is not None:
        sql += request.form.get('unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('new_unit_price') is not None:
        sql += request.form.get('new_unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('diff_unit_price') is not None:
        sql += request.form.get('diff_unit_price')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('status') is not None:
        sql += request.form.get('status')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('supplier_name') is not None:
        sql += request.form.get('supplier_name')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('stock_reference') is not None:
        sql += request.form.get('stock_reference')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('cutting_assembly') is not None:
        sql += request.form.get('cutting_assembly')
    sql += "'"

    sql += ','

    sql += "'"
    if request.form.get('detail') is not None:
        sql += request.form.get('detail')
    sql += "'"

    sql += ")";

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "add masterdata":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_formula/delete', methods=['POST'])
def get_masterformula_delete():
    app.logger.info('/master_formula/delete')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "delete from master_tsubakimoto_formula"
    sql += " where Id="
    sql += request.form.get('Id')

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "delete masterformula with id":
            {
                "result": "pass"
            }
    }
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

@app.route('/exchange_rate/deleteall', methods=['POST'])
def get_exchangerate_deleteall():
    app.logger.info('/exchange_rate/deleteall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('delete from exchange_rate')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    data = {
        "status":"true",
        "delete all exchange_rate":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/exchange_rate/update', methods=['POST'])
def get_exchangerate_update():
    app.logger.info('/exchange_rate/update')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "update exchange_rate set "

    if request.form.get('usd_br') is not None:
        sql += ","
        sql += "usd_br="
        sql += request.form.get('usd_br')

    if request.form.get('usd_cr') is not None:
        sql += ","
        sql += "usd_cr="
        sql += request.form.get('usd_cr')

    if request.form.get('usd_qr') is not None:
        sql += ","
        sql += "usd_qr="
        sql += request.form.get('usd_qr')

    if request.form.get('usd_pr') is not None:
        sql += ","
        sql += "usd_pr="
        sql += request.form.get('usd_pr')

    if request.form.get('eur_br') is not None:
        sql += ","
        sql += "eur_br="
        sql += request.form.get('eur_br')

    if request.form.get('eur_cr') is not None:
        sql += ","
        sql += "eur_cr="
        sql += request.form.get('eur_cr')

    if request.form.get('eur_qr') is not None:
        sql += ","
        sql += "eur_qr="
        sql += request.form.get('eur_qr')

    if request.form.get('eur_pr') is not None:
        sql += ","
        sql += "eur_pr="
        sql += request.form.get('eur_pr')

    if request.form.get('jpy_br') is not None:
        sql += ","
        sql += "jpy_br="
        sql += request.form.get('jpy_br')

    if request.form.get('jpy_cr') is not None:
        sql += ","
        sql += "jpy_cr="
        sql += request.form.get('jpy_cr')

    if request.form.get('jpy_qr') is not None:
        sql += ","
        sql += "jpy_qr="
        sql += request.form.get('jpy_qr')

    if request.form.get('jpy_pr') is not None:
        sql += ","
        sql += "jpy_pr="
        sql += request.form.get('jpy_pr')

    if request.form.get('rate_remark') is not None:
        sql += ","
        sql += "rate_remark="
        sql += request.form.get('rate_remark')

    if request.form.get('file_name') is not None:
        sql += ","
        sql += "file_name="
        sql += request.form.get('file_name')

    if request.form.get('rate_path') is not None:
        sql += ","
        sql += "rate_path="
        sql += request.form.get('rate_path')

    sql += " where rate_id="
    sql += request.form.get('rate_id')

    sql = sql.replace("update exchange_rate set ,", "update exchange_rate set ");

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "update exchange_rate":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/exchange_rate/delete', methods=['POST'])
def get_exchangerate_delete():
    app.logger.info('/exchange_rate/delete')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "delete from exchange_rate"
    sql += " where rate_id="
    sql += request.form.get('rate_id')

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "delete exchange_rate by id":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/exchange_rate/add', methods=['POST'])
def get_exchangerate_add():
    app.logger.info('/exchange_rate/add')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "insert into exchange_rate(usd_br,usd_cr,usd_pr,usd_qr,eur_br,eur_cr,eur_qr,eur_pr,jpy_br,jpy_cr,jpy_pr,jpy_qr,rate_remark,rate_file_name,rate_path)";
    sql += " values ("

    if request.form.get('usd_br') is not None:
       sql += request.form.get('usd_br')
    else:
       sql += "null"

    sql += ","

    if request.form.get('usd_cr') is not None:
        sql += request.form.get('usd_cr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('usd_pr') is not None:
        sql += request.form.get('usd_pr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('usd_qr') is not None:
        sql += request.form.get('usd_qr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('eur_br') is not None:
        sql += request.form.get('eur_br')
    else:
        sql += "null"

    sql += ","

    if request.form.get('eur_cr') is not None:
        sql += request.form.get('eur_cr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('eur_qr') is not None:
        sql += request.form.get('eur_qr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('eur_pr') is not None:
        sql += request.form.get('eur_pr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('jpy_br') is not None:
        sql += request.form.get('jpy_br')
    else:
        sql += "null"

    sql += ","

    if request.form.get('jpy_cr') is not None:
        sql += request.form.get('jpy_cr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('jpy_pr') is not None:
        sql += request.form.get('jpy_pr')
    else:
        sql += "null"

    sql += ","

    if request.form.get('jpy_qr') is not None:
        sql += request.form.get('jpy_qr')
    else:
        sql += "null"

    sql += ","

    sql += "'"
    if request.form.get('rate_remark') is not None:
        sql += request.form.get('rate_remark');
    sql += "'"

    sql += ","

    sql += "'"
    if request.form.get('rate_file_name') is not None:
        sql += request.form.get('rate_file_name');
    sql += "'"

    sql += ","

    sql += "'"
    if request.form.get('rate_path') is not None:
        sql += request.form.get('rate_path');
    sql += "'"

    sql += ")"

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "add exchange_rate":
            {
                "result": "pass"
            }
    }
    return jsonify(data)

@app.route('/master_history/listall', methods=['POST'])
def get_masterhistory_listall():
    app.logger.info('/master_history/listall')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute('select * from master_pricelist_history')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/master_history/add', methods=['POST'])
def get_masterhistory_add():
    app.logger.info('/master_history/add')
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    sql = "insert into master_pricelist_history(master_file_name,file_path)"
    sql += " values ("

    if request.form.get('master_file_name') is not None:
        sql += "'" + request.form.get('master_file_name') + "'"
    else:
        sql += "null"

    sql += ","

    if request.form.get('file_path') is not None:
        sql += "'" + request.form.get('file_path') + "'";
    else:
        sql += "null";

    sql += ")"

    print('sql='+sql)

    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

    data = {
        "status":"true",
        "add master_history":
            {
                "result": "pass"
            }
    }
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
