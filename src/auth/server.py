import jwt, datetime, os, bcrypt
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL


server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

@server.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO user (email, password) VALUES (%s, %s)", (email, hashed_password))
        mysql.connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return jsonify({"message": "Missing credentials"}), 400
    
    cur = mysql.connection.cursor()
    try:
        res = cur.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))
        if res > 0:
            user_row = cur.fetchone()
            email, password_hash = user_row

            if auth.username == email and bcrypt.checkpw(auth.password.encode('utf-8'), password_hash.encode('utf-8')):
                return jsonify({"token": createJWT(auth.username, os.environ.get("JWT_SECRET"), True)})
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return jsonify({"message": "Missing credentials"}), 400
    
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
        return jsonify(decoded), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 403

def createJWT(username, secret, u_type):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "admin": u_type
        },
        secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)