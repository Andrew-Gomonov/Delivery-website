import math
import os
import bcrypt
import jwt
from flask import session, current_app
from werkzeug.utils import secure_filename
from hashlib import md5
from App import cur, conn
from App.core.tokens import generate_auth_token
from App.core.utils import validate_image
from App.errors.api import APIAuthError, APIBadRequestError


def login(data: dict):
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise APIAuthError("No username or password sent")

    cur.execute(f"SELECT id,password FROM Users WHERE email='{email}'")
    user = cur.fetchone()
    csrf_token = session.pop('csrf_token', None)
    if not user:
        raise APIAuthError("User with this email not found")
    if not bcrypt.checkpw(password.encode(), user[1].encode()):
        raise APIAuthError("Wrong password")
    if data.get('csrf_token') != csrf_token or not csrf_token:
        raise APIAuthError("CSRF token missing or incorrect")
    token = generate_auth_token(user[0])
    return token


def get_next_last_user_id():
    cur.execute("SELECT MAX(id) FROM Users")
    max_id = cur.fetchone()
    if not max_id:
        return 1
    else:
        return max_id[0] + 1


def get_delivery_history(courier_id):
    cur.execute("SELECT customer_address,date_placed FROM Orders WHERE courier_id=%s", (courier_id,))
    delivery_history = cur.fetchall()
    return delivery_history


def create_user(data_user: dict) -> bool:
    """
    Create user by a dictionary
    :param data_user: this is a dictionary that should contain the keys name, email, password, is_admin
    :return: code and message
    """
    for key in data_user.keys():
        if key not in ['name', 'email', 'password', 'is_admin', 'profile_picture', 'phone']:
            raise APIBadRequestError("Unknown key in user dictionary")
    cur.execute(f"SELECT id FROM Users WHERE email='{data_user['email']}'")
    user = cur.fetchone()
    if user is not None:
        raise APIBadRequestError("A user with this email already exists")
    hashed_password = bcrypt.hashpw(data_user['password'].encode(), bcrypt.gensalt())
    sql = """INSERT INTO Users (`name`, `password`, `email`,`register_date`,`is_admin`,`profile_picture`,`phone`)
             VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s,%s,%s);
          """
    cur.execute(sql,
                (
                    data_user['name'],
                    hashed_password.decode(),  # we decode the bytes, because in the database we need a string
                    data_user['email'],
                    data_user['is_admin'],
                    data_user['profile_picture'],
                    data_user['phone']
                )
                )
    conn.commit()
    return True


def validate_user_data(request, user, is_admin=False):
    new_user_data = {}
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    if name != user.name and name:
        new_user_data['name'] = name
    if is_admin:
        form_is_admin = request.form.get('is_admin')
        is_admin = 1 if form_is_admin is not None else 0
        if user.is_admin != is_admin:
            new_user_data['is_admin'] = is_admin
    if phone != user.phone and phone:
        new_user_data['phone'] = phone

    if email != user.email and email:
        new_user_data['email'] = email

    if password:
        if password == password_confirm:
            if not bcrypt.checkpw(password.encode(), user.password.encode()):
                new_user_data['password'] = password
            else:
                raise APIBadRequestError("You used a previous password")
        else:
            raise APIBadRequestError("Passwords do not match")
    # Check if a file was uploaded and file is not empty
    if 'photo' in request.files:
        # Get the uploaded file
        photo = request.files['photo']
        filename = secure_filename(request.files['photo'].filename)
        # Check file name is not empty
        if filename != '':
            # Get the size of the photo
            photo_length = len(photo.read())
            photo.seek(0)
            photo_ext = os.path.splitext(filename)[1]
            # check that the image is the right size for us
            if photo_length < current_app.config['MAX_SIZE_PHOTO']:
                # Checking if a file is an image
                if photo.content_type.startswith('image') \
                        and photo_ext in current_app.config['UPLOAD_EXTENSIONS'] \
                        and photo_ext == validate_image(photo.stream):
                    new_photo_name = md5(str(user.id).encode()).hexdigest()
                    photo.save(os.path.join('App/static/avatars', new_photo_name))
                    new_user_data['profile_picture'] = "avatars/" + new_photo_name
                else:
                    raise APIBadRequestError("Only images are allowed")
            else:
                return APIBadRequestError("Photo is too large")
    if not new_user_data:
        raise APIBadRequestError("user data has not changed")
    return new_user_data


def get_total_pages(per_page):
    cur.execute("SELECT COUNT(*) FROM Users")
    total_rows = cur.fetchone()[0]
    return math.ceil(total_rows / per_page)


def get_users(page, per_page) -> list[dict[str, str]]:
    """
    Get all users in database
    :return: returns a list of dictionaries that contain
    id,name,email,hash password,registration date,is admin(1 - yes,0 - no)
    """
    users = []
    if page and per_page:
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM Users ORDER BY register_date DESC LIMIT %s OFFSET %s", (per_page, offset))
    else:
        cur.execute("SELECT * from Users")
    users_info = cur.fetchall()
    if users_info:
        for user in users_info:
            users.append({
                "id": user[0],
                "name": user[1],
                "password": user[2],
                "email": user[3],
                "register_datetime": str(user[4]),
                "is_admin": user[5],
                "profile_picture": user[6],
                "phone": user[7]
            })
    return users


def is_authenticated():
    token = session.get('token')
    if not token:
        return False
    try:
        user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    except jwt.exceptions.InvalidTokenError:
        return False
    cur.execute(f"select * from Users where id='{user_id}'")
    info = cur.fetchone()
    if info is None:
        return False
    return True
