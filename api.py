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


@app.route("/book/<int:id>/loan", methods=["GET"])
def get_loans_by_book(id):
    data = data_fetch(
        """
        SELECT Member.FirstName, Member.LastName, Loan.LoanDate, Loan.ReturnDate 
        FROM Loan
        INNER JOIN Member
        ON Loan.MemberID = Member.MemberID
        WHERE Loan.BookID = {}
        """.format(id)
    )
    return make_response(
        jsonify({"book_id": id, "count": len(data), "loans": data}), 200
    )


if __name__ == "__main__":
    app.run(debug=True)
