from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "final_drill"

app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


@app.route("/book", methods=["GET"])
def get_department():
    data = data_fetch("""select * from book""")
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>", methods=["GET"])
def get_book_by_id(id):
    data = data_fetch("""SELECT * FROM book where BookID = {}""".format(id))
    return make_response(jsonify(data), 200)

@app.route("/book/<int:id>/loan", methods=["GET"])
def get_loans_by_book(id):
    data = data_fetch(
        """
        SELECT book.BookID, book.Title, book.Author, book.Publisher, book.Year, loan.MemberID
        FROM book
        INNER JOIN loan
        ON book.BookID = loan.BookID
        WHERE book.BookID = {}
        """.format(id)
    )
    return make_response(
        jsonify({"book_id": id, "count": len(data), "loans": data}), 200
    )

@app.route("/book", methods=["POST"])
def add_member():
    cur = mysql.connection.cursor()
    info = request.get_json()
    BookID = info["BookID"]
    Title = info ["Title"]
    Author = info["Author"]
    Publisher = info ["Publisher"]
    Year = info ["Year"]
    cur.execute(
        """ INSERT INTO book (BookID, Title, Author, Publisher, Year) VALUE (%s, %s, %s, %s, %s)""",
        (BookID, Title, Author, Publisher, Year ),
    )
    mysql.connection.commit()
    print("row(s) affected :{}".format(cur.rowcount))
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "book added successfully", "rows_affected": rows_affected}
        ),
        201,
    )

@app.route("/book/<int:id>", methods=["PUT"])
def update_book(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    BookID = info ["BookID"]
    Title = info ["Title"]
    Author = info ["Author"]
    Publisher = info ["Publisher"]
    Year  = info ["Year"]
    cur.execute(
        """ UPDATE book SET BookID = %s, Title = %s, Author = %s, Publisher = %s, Year = %s WHERE BookID = %s """,
        (BookID, Title, Author, Publisher, Year, id),
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "book updated successfully", "rows_affected": rows_affected}
        ),
        200,
    )

if __name__ == "__main__":
    app.run(debug=True)
