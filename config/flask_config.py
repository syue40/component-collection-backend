from flask import Flask, g
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from psycopg2 import pool

load_dotenv()
app = Flask(__name__)

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)

# Allowing cross origin requests since the frontend is in React
CORS(app, origins=["*"])

# Secret key that will be used to encrypt tokens.
app.config["JWT_SECRET_KEY"] = "Sean"

# Tokens expiry time set to 2 hours.
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["DEBUG"] = True

# Required credentials for sending emails
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

app.config["DEBUG"] = True
jwt = JWTManager(app)
mail = Mail(app)

try:
    # Creating a connection pool with minimum 1 and maximum 20 connections
    app.config["postgreSQL_pool"] = pool.SimpleConnectionPool(
        1,
        20,
        database=os.getenv("database"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("hostDB"),
    )

    print("Successfully connected to db!")

except Exception as e: # pylint: disable=broad-except
    print("Problem connecting to db.", e)


def get_db():
    print("GETTING CONN")
    if "db" not in g:
        g.db = app.config["postgreSQL_pool"].getconn()
    return g.db


@app.teardown_appcontext
def close_conn(e):
    print("CLOSING CONN")
    db = g.pop("db", None)
    if db is not None:
        app.config["postgreSQL_pool"].putconn(db)
