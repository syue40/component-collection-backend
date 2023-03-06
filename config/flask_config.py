from flask import Flask, g
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import uuid
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import pool

load_dotenv()
app = Flask(__name__)

# Allowing cross origin requests since the frontend is in React
CORS(app, origins=["*"])

# Secret key that will be used to encrypt tokens.
app.config["JWT_SECRET_KEY"] = "Sean"

# Tokens expiry time set to 2 hours.
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

app.config["DEBUG"] = True
jwt = JWTManager(app)
mail = Mail(app)

try:
    # Creating a connection pool with minimum 1 and maximum 20 connections
    app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(1, 20,
                                                                       database=os.getenv(
                                                                           'database'),
                                                                       user=os.getenv(
                                                                           'user'),
                                                                       password=os.getenv(
                                                                           'password'),
                                                                       host=os.getenv('hostDB'))

    print("Successfully connected to db!")

except Exception as e:
    print("Problem connecting to db.", e)


def get_db():
    print('GETTING CONN')
    if 'db' not in g:
        g.db = app.config['postgreSQL_pool'].getconn()
    return g.db


@app.teardown_appcontext
def close_conn(e):
    print('CLOSING CONN')
    db = g.pop('db', None)
    if db is not None:
        app.config['postgreSQL_pool'].putconn(db)
