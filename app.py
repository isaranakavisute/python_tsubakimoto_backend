from flask import Flask, jsonify, request
#from flaskext.mysql import MySQL
import mysql.connector.pooling
from datetime import datetime


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
    port=3306,  #3307
    database="akt1" #tsubakimoto test
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
def get_masterdata_upload():
    app.logger.info('/master_data/upload')
    
    # conn = connection_pool.get_connection()
    # cursor = conn.cursor()
    # cursor.execute('select * from exchange_rate')
    # data = cursor.fetchall()
    # cursor.close()
    # conn.close() 
    
    file = request.files['file']
    fullfilename = file.filename
    onlyfilename = fullfilename.split('.')[0];
    onlyfileext = fullfilename.split('.')[1];
    app.logger.info(file);
    app.logger.info("uploaded file name : "+file.filename)
    print(request.files);
    newpath = 'uploaded_files/' + onlyfilename  + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.' + onlyfileext;
    app.logger.info("uploaded new file path : "+newpath)
    file.save(newpath)
    
    
    data = { 
             "status":"true",
             "upload_excel":
                   {
                    "result": "pass",
                    "full uploaded file path": newpath
                   }
           } 
    
    return jsonify(data)
    
# In-memory data store
items = [{"id": 1, "name": "This is item 1"}, {"id": 2, "name": "This is item 2"}]

# GET request: Retrieve all items
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items)

# GET request: Retrieve a specific item by ID
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)

# POST request: Create a new item
@app.route('/api/items', methods=['POST'])
def create_item():
    new_item = {"id": len(items) + 1, "name": request.json.get('name')}
    items.append(new_item)
    return jsonify(new_item), 201

# PUT request: Update an existing item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    item['name'] = request.json.get('name', item['name'])
    return jsonify(item)

# DELETE request: Delete an item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item["id"] != item_id]
    return '', 204

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0',debug=True)
