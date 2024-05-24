from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import dicttoxml
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "final_drill"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["JWT_SECRET_KEY"] = 'password224'  # Change this to a strong secret key

mysql = MySQL(app)
jwt = JWTManager(app)

# Helper function to convert data to the desired format
def output_format(data, format='json'):
    if format == 'xml':
        xml_data = dicttoxml.dicttoxml(data, custom_root='result', attr_type=False)
        # Convert XML to string and prettify
        xml_pretty = ET.tostring(ET.fromstring(xml_data), encoding='utf8', method='xml')
        return Response(xml_pretty, mimetype='application/xml')
    else:  # Default to JSON
        return jsonify(data)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # TODO: Validate username and password against your user database
    if username == 'admin' and password == 'password224':  # Replace with real user validation
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

def data_fetch(query, params=None):
    cur = mysql.connection.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

@app.route("/book", methods=["GET"])
def get_book():
    data = data_fetch("""SELECT * FROM book""")
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>", methods=["GET"])
def get_book_by_id(id):
    data = data_fetch("""SELECT * FROM book WHERE BookID = %s""", (id,))
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>/loan", methods=["GET"])
def get_loans_by_book(id):
    data = data_fetch(
        """
        SELECT book.BookID, book.Title, book.Author, book.Publisher, book.Year, loan.MemberID, loan.LoanDate, loan.ReturnDate
        FROM book
        INNER JOIN loan ON book.BookID = loan.BookID
        WHERE book.BookID = %s
        """, (id,)
    )
    return make_response(jsonify({"BookID": id, "count": len(data), "loans": data}), 200)

@app.route("/book", methods=["POST"])
def add_book():
    cur = mysql.connection.cursor()
    info = request.get_json()
    BookID = info["BookID"]
    Title = info["Title"]
    Author = info["Author"]
    Publisher = info["Publisher"]
    Year = info["Year"]
    cur.execute(
        """INSERT INTO book (BookID, Title, Author, Publisher, Year) VALUES (%s, %s, %s, %s, %s)""",
        (BookID, Title, Author, Publisher, Year)
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "book added successfully", "rows_affected": rows_affected}), 201)

@app.route("/book/<int:id>", methods=["PUT"])
def update_book(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    BookID = info["BookID"]
    Title = info["Title"]
    Author = info["Author"]
    Publisher = info["Publisher"]
    Year = info["Year"]
    cur.execute(
        """UPDATE book SET BookID = %s, Title = %s, Author = %s, Publisher = %s, Year = %s WHERE BookID = %s""",
        (BookID, Title, Author, Publisher, Year, id)
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "book updated successfully", "rows_affected": rows_affected}), 200)

@app.route("/book/<int:id>", methods=["DELETE"])
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM book WHERE BookID = %s""", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "book deleted successfully", "rows_affected": rows_affected}), 200)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == "__main__":
    app.run(debug=True)
