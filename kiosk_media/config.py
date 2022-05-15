# various configurations for the kiosk
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import random

users_fname = None

def json_read(fname):
    try:
        with open(fname) as fp:
            data = fp.read()
    except:
        return {}

    try:
        my_json = json.loads(data)
    except:
        my_json = {}
    return my_json

def json_write(my_json, fname):
    data = json.dumps(my_json)
    with open(fname, 'w') as fp:
        fp.write(data)

    return True

def set_users_file(fname):
    global users_fname
    users_fname = fname

def get_users_fname():
    if users_fname is None:
        raise ValueError("config module requires setting BASE_DIR and users_fname")
    return users_fname

def user_add(username, password):
    fname = get_users_fname()
    users = json_read(fname)
    users[username] = generate_password_hash(password)
    json_write(users, fname)
    return True

def user_del(username):
    """deactivate user"""
    users = json_read(fname)
    try:
        del users[username]
        return True
    except:
        pass
    return False
    
def check_login(username, password):
    fname = get_users_fname()
    users = json_read(fname)
    if username in users:
        pwhash = users[username]
        if check_password_hash(pwhash, password):
            return True
    return False

def authenticate(token):
    if token == signature:
        return True
    return False

secret_key = 'EUD87sh&9ehis$64A2(*sA'
development = False
signature = secret_key