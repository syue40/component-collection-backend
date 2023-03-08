"""
This module has different functions to validate the data that is passed to it using Cerberus library.
"""
from cerberus import Validator


def validate_email(email):
    schema = {
        "email": {
            "type": "string",
            "regex": '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        }
    }
    doc = {"email": email}
    validator = Validator(schema)
    return validator.validate(doc)


def validate_pass(password):
    """
    Defines a schema of correct type of data, compares it to data passed to it.
    Returns a true boolean value if email and password are in correct shape.
    """
    schema = {
        "password": {
            "type": "string",
            "regex": '^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])([a-zA-Z0-9@$!%*?&]{8,30})$'
            # Regex for 8 character password including uppercase, lowercase and numbers
        }
    }
    doc = {"password": password}
    validator = Validator(schema)
    return validator.validate(doc)


def validate_signup_data(data_list):
    """
    Defines a schema of correct type of data, compares it to data passed to it.
    Returns a boolean value if data list argument is in correct shape.
    """
    schema = {
        "email": {
            "type": "string",
            "minlength": 3,
            "regex": '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        }
    }
    doc = {
        "email": data_list[0],
    }
    validator = Validator(schema)
    return validator.validate(doc)
