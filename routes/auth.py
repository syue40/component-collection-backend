from flask import Blueprint, jsonify, request, Response
from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, decode_token
from utils.dao import get_user, add_user, update_user_details
from utils.validator import validate_email, validate_signup_data, validate_pass
import requests
import os
from config.flask_config import get_db, jwt
from datetime import timedelta, datetime

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['GET','POST'])
def login():
    # Extract data from the request
    email = request.json['email'].lower()
    password = request.json['password']

    # Check if email and password are in correct shape.
    if not validate_email(email):
        return jsonify(x="Invalid email, please check format")

    try:
        # Searches to find user in DB
        conn = get_db()
        record = get_user(email, conn)
        # Checks if account is found
        if record:
            if sha256_crypt.verify(password, record['password']):
                access_token = create_access_token(identity=email)
                res = {
                    "account_found": True,
                    "login": True,
                    "email": email,
                    "access_token": access_token,
                }
            else:
                res = {
                    "account_found": True,
                    "login": False
                }
        else:
            res = {
                "account_found": False,
                "login": False
            }
        return res
    except Exception as e:
        return e


@auth.route('/signup', methods=['GET','POST'])
def signup():
    
    email = request.json['email'].lower()
    password = request.json['password']

    if not validate_email(email):
        res = jsonify({"error": "Invalid email format."})
        return res
    if not validate_pass(password):
        res = jsonify(
            {"error": "Invalid password format: passwords must contain an upper and lower case character, a number, and a special character."})
        return res

    hashed_password = sha256_crypt.encrypt(password)
    data_list = [email, password]

    # if account number is not empty
    conn = get_db()
    result = add_user([email, hashed_password], conn)
    if result == True:
        access_token = create_access_token(identity=email)
        res = {
            "user_added": True,
            "access_token": access_token
        }
    else:
        res = {
            "user_added": False,
            "error": "Account number doesn't exist. Please contact us to resolve this issue."
        }
    return res

@auth.route('/update-profile', methods=['POST'])
@jwt_required()
def update_profile():
    jwt_token = get_jwt()
    email = jwt_token['sub']
    first_name = request.json['firstName']
    last_name = request.json['lastName']
    biography = request.json['biography']
    
    conn = get_db()
    result = update_user_details(
        first_name, last_name, biography, email, conn)
    if result:
        return jsonify({"success": True})
    else:
        return jsonify({"alert": True, "msg": "Issue."})

@auth.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
