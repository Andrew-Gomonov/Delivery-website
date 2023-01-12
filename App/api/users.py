import bcrypt
import jwt
from flask import request, redirect, url_for
from App.api.tokens import generate_auth_token
from App.errors.api import APIAuthError, APINotFoundError, APIUnknownKeyError
from functools import wraps
from App import cur, conn,  app


def only_admins(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['sub']
        user = User(user_id)
        if user.is_admin != 1:
            return redirect(url_for('user_page'))
        return f(*args, **kwargs)
    return decorated


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if token is None:
            return redirect(url_for('login_page'))
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.exceptions.InvalidTokenError:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


def login(data):
    email = data['email']
    password = data['password']
    if not email and not password:
        raise APIAuthError("Username or password not sent")

    cur.execute(f"SELECT id,password FROM Users WHERE email='{email}'")
    user = cur.fetchone()
    if not user:
        raise APIAuthError("User with this email not found")
    if not bcrypt.checkpw(password.encode(), user[1].encode()):
        raise APIAuthError("Wrong password")
    token = generate_auth_token(user[0])
    return token


def create_user(data_user: dict) -> bool:
    """
    Create user by a dictionary
    :param data_user: this is a dictionary that should contain the keys name, email, password, is_admin
    :return: code and message
    """
    for key in data_user.keys():
        if key not in ['name', 'email', 'password', 'is_admin']:
            raise APIUnknownKeyError("Unknown key in user dictionary")
    hashed_password = bcrypt.hashpw(data_user['password'].encode(), bcrypt.gensalt())
    cur.execute(
        "INSERT INTO Users (name, email, password,register_date,is_admin)"
        "VALUES ('{0}', '{1}', \"{2}\", CURRENT_TIMESTAMP, {3});"
        .format(
            data_user['name'], data_user['email'],
            hashed_password.decode(),  # we decode the bytes, because in the database we need a string
            data_user['is_admin']
        )
    )
    conn.commit()
    return True


def get_users() -> list[dict[str, str]]:
    """
    Get all users in database
    :return: returns a list of dictionaries that contain
    id,name,email,hash password,registration date,is admin(1 - yes,0 - no)
    """
    json_data = []
    cur.execute("SELECT * from Users")
    users_array = cur.fetchall()
    for user in users_array:
        json_data.append({
            "id": user[0],
            "name": user[1],
            "password": user[2],
            "email": user[3],
            "date": str(user[4]),
            "is_admin": user[5],
            "profile_picture": user[6]
        })
    return json_data


def search_users(data_to_search: dict[str, str]):
    for key in data_to_search.keys():
        if key not in ['name', 'email', 'password', 'is_admin']:
            raise APIUnknownKeyError("Unknown key in url")
    result = ""
    for key, value in data_to_search.items():
        if not value.isnumeric():
            result += f"{key} LIKE('%{value}%') AND "
        else:
            result += f"{key} = '{value}' AND "

    result = result[:-5]
    json_data = []
    cur.execute(f"SELECT * from Users WHERE {result};")
    users_array = cur.fetchall()
    if len(users_array) == 0:
        raise APIAuthError("Users not found in database")
    for user in users_array:
        json_data.append({
            "id": user[0],
            "name": user[1],
            "password": user[2],
            "email": user[3],
            "date": str(user[4]),
            "is_admin": user[5],
            "profile_picture": user[6]
        })
    return json_data


class User:
    """
    User crud(crud - create, read, update, delete)
    """
    id = 0
    name = ""
    password = ""
    email = ""
    datetime = ""
    is_admin = 0
    profile_picture = ""

    # Constructor
    def __init__(self, user_id: int):
        cur.execute(f"select * from Users where id='{user_id}'")
        info = cur.fetchone()
        if info is None:
            raise APINotFoundError("User not found in database")
        self.user_id = user_id
        User.id = info[0]
        User.name = info[1]
        User.password = info[2]
        User.email = info[3]
        User.datetime = str(info[4])
        User.is_admin = info[5]
        User.profile_picture = info[6]

    def __repr__(self):
        return f'<User {User.name}>'

    @staticmethod
    def to_dict():
        """
        Get user information by id
        :return: dictionary that contain id,name,email,
        password,registration date,is admin(1 - yes,0 - no),profile_picture
        """
        json_data = {}
        json_data.update({
            "id": User.id,
            "name": User.name,
            "password": User.password,
            "email": User.email,
            "datetime": User.datetime,
            "is_admin": User.is_admin,
            "profile_picture": User.profile_picture,
        })
        return json_data

    def delete(self) -> bool:
        """
        Delete user by id
        :return: code and message
        """
        cur.execute(f"DELETE FROM Users WHERE id='{self.user_id}'")
        conn.commit()
        return True

    def edit(self, data_to_edit: dict) -> bool:
        """
        Edit user by dictionary
        :param data_to_edit: this is a dictionary in which there should be data to change
        :return: code and message
        """
        for key in data_to_edit.keys():
            if key not in ['name', 'email', 'password', 'is_admin', 'profile_picture']:
                raise APIUnknownKeyError("Unknown key in  user dictionary")
        if 'password' in data_to_edit.keys():
            data_to_edit['password'] = bcrypt.hashpw(data_to_edit['password'].encode(), bcrypt.gensalt()).decode()
        result = ""
        for key, value in data_to_edit.items():
            result += f"{key} = '{value}',"
        result = result[:-1]
        cur.execute(f"UPDATE Users SET {result} WHERE id='{self.user_id}'")
        conn.commit()
        return True
