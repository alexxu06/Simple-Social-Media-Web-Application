from app import app
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from app import db
from app.models import User, Post
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import json

@app.after_request
def refresh_expiring_tokens(response):
    try:
        expiration_time = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        time_to_refresh = datetime.timestamp(now + timedelta(minutes=0.2))
        if time_to_refresh > expiration_time:
            access_token = create_access_token(identity=get_jwt_identity(), additional_claims={"admin": get_jwt("admin")})
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    admin = request.json.get("admin", None)

    user = User(email=email, username=username, admin=admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user, additional_claims={"admin": user.admin})
    set_access_cookies("success", access_token)

    return jsonify({"msg": "successfully signed up", "token": access_token})

    

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by((email==email) | (username==username)).one_or_none()

    if not user or user_by_username:
        return "User does not exist", 401

    if not user.check_password(password):
        return "Wrong password", 401
    
    access_token = create_access_token(identity=user, additional_claims={"admin": user.admin})
    set_access_cookies("success", access_token)
    return jsonify({"msg": "successfully logged in", "token": access_token})

@app.route("/logout", methods=["POST"])
def logout():
    response = {"msg": "logout successfully"}
    unset_jwt_cookies(response)
    return response


@app.route("/home", methods=["GET"])
@jwt_required()
def home():
    username = current_user.username

    if get_jwt("admin"):
        return jsonify({"msg": "Welcome {username}, you are a admin!"})
    else:
        return "Welcome {username}!"
    