from flask import Blueprint, jsonify, request, Response
from passlib.hash import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, decode_token
from utils.dao import get_user, add_user, update_user_details, update_password
from utils.validator import validate_email, validate_signup_data, validate_pass
from utils.email import send_email
import requests
import os
from config.flask_config import get_db, jwt
from datetime import timedelta, datetime

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['POST'])
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
                    "login": False,
                    "alert": "Incorrect password, please try again.",
                }
        else:
            res = {
                "account_found": False,
                "login": False,
                "alert": "Account does not exist."
            }
        return res
    except Exception as e:
        return e


@auth.route('/signup', methods=['POST'])
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
    try:
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
                "error": "Account Already Exists"
            }
    except:
        print("Error Adding User")
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
        return jsonify({"alert": True, "msg": "Issue changing profile."})

@auth.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@auth.route('/change-password', methods=["POST"])
@jwt_required()
def change_password():
    email = get_jwt_identity()
    password = request.json['oldPassword']
    new_password = request.json['newPassword']
    new_password_confirm = request.json['newPasswordVerify']
    conn = get_db()
    record = get_user(email, conn)

    if record and sha256_crypt.verify(password, record['password']):
        if new_password_confirm != new_password:
            return jsonify({"password_error": "Passwords do not match"})
        elif not validate_pass(new_password):
            return jsonify({"password_error": "Password must be at least 8 characters, and contain at least one uppercase, lowercase, numeric, and special character."})
        try:
            update_password(sha256_crypt.encrypt(new_password), email, conn)
            return jsonify({"success": "Password successfully updated!"})
        except:
            return jsonify({"password_error": "Unable to update password"})
    elif not sha256_crypt.verify(password, record['password']):
        return jsonify({"password_error": "Old password is incorrect"})
    else:
        return jsonify({"password_error": "Problem fetching user record"})


@auth.route('/reset-password', methods=["POST"])
def reset_password():
    recipient = request.json["email"]
    try:
        conn = get_db()
        user_exists = get_user(recipient, conn)
        if not user_exists:
            return jsonify({"user_exists": False})
        access_token = create_access_token(
            identity=recipient, expires_delta=timedelta(minutes=30))
        send_email(recipient, "forgot_password", "", access_token)
    except:
        print("Error resetting password")
    return jsonify({"sent": True})

@auth.route('/reset-password-post', methods=['POST'])
def reset_password_post():
    data = request.json['password']
    new_password = data['new_password']
    identification = decode_token(data['resetToken'], allow_expired=True)
    email = identification['sub']
    conn = get_db()

    if not validate_pass(new_password):
        return jsonify({"alert": True, "message": "Password must be at least 8 characters, and contain at least one uppercase, lowercase, numeric, and special character."})
    try:
        update_password(sha256_crypt.encrypt(new_password), email, conn)
        return jsonify({"message": "Password successfully reset. You can now login with the new password!"})
    except:
        return jsonify({"alert": True, "message": "Unable to update password"})