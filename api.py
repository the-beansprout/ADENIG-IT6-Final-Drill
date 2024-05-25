from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root" 
app.config["MYSQL_DB"] = "final_drill"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["SECRET_KEY"] = 'admin224' 

mysql = MySQL(app)

# Security
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            token = token.split(" ")[1]  
            print(f"Decoded token: {token}")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(f"Decoded data: {data}")
        except Exception as e:
            print(f"Token decode error: {str(e)}")
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if auth and auth.username == "admin" and auth.password == "breina_adenig":  
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        print(f"Generated token: {token}")
        return jsonify({'token': token})
    return make_response("Could not verify!", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})



def data_fetch(query, params=None):
    cur = mysql.connection.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

# READ
@app.route("/book", methods=["GET"])
@token_required
def get_book():
    data = data_fetch("""SELECT * FROM book""")
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>", methods=["GET"])
@token_required
def get_book_by_id(id):
    data = data_fetch("""SELECT * FROM book WHERE BookID = %s""", (id,))
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>/loan", methods=["GET"])
@token_required
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

# ADD
@app.route("/book", methods=["POST"])
@token_required
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

# UPDATE
@app.route("/book/<int:id>", methods=["PUT"])
@token_required
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

# DELETE
@app.route("/book/<int:id>", methods=["DELETE"])
@token_required
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM book WHERE BookID = %s""", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(jsonify({"message": "book deleted successfully", "rows_affected": rows_affected}), 200)

if __name__ == "__main__":
    app.run(debug=True)
