import os
import bcrypt
import jwt
from werkzeug.utils import secure_filename
from hashlib import md5
from App.api.news import get_news, News
from App.api.users import User, login, auth_required, only_admins
from App.api.utils import validate_image
from App.errors.api import APIAuthError
from flask import render_template, request, make_response, redirect, url_for
from App import app


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        try:
            auth_token = login(request.form)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('token', auth_token, httponly=True, samesite="strict")
            return resp
        except APIAuthError as error:
            return render_template('users/login.html', error=error.message)
    else:
        return render_template('users/login.html')


@app.route('/create-new-order')
@auth_required
@only_admins
def create_new_order():
    return render_template("admins/create-new-order.html")


@app.route('/me')
@auth_required
def user_page():
    user_id = jwt.decode(request.cookies.get('token'), app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    user = User(user_id)
    return render_template("users/user-page.html", user=user)


@app.route('/chat')
@auth_required
def chat_page():
    return render_template("users/chat.html")


@app.route('/change-profile', methods=['GET', 'POST'])
@auth_required
def change_profile():
    user_id = jwt.decode(request.cookies.get('token'), app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    user = User(user_id)
    if request.method == "GET":
        return render_template("users/change-profile.html", user=user)
    else:
        new_user_data = {}
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        if name != user.name and name != "":
            new_user_data['name'] = name

        if email != user.email and email != "":
            new_user_data['email'] = email

        if password:
            if password == password_confirm:
                if not bcrypt.checkpw(password.encode(), user.password.encode()):
                    new_user_data['password'] = password
                else:
                    return render_template(
                        "users/change-profile.html", user=user, error="You used a previous password"
                    )
            else:
                return render_template(
                    "users/change-profile.html", user=user, error="Passwords do not match"
                )
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
                if photo_length < app.config['MAX_SIZE_PHOTO']:
                    # Checking if a file is an image
                    if photo.content_type.startswith('image') and photo_ext in app.config['UPLOAD_EXTENSIONS']  \
                            and photo_ext == validate_image(photo.stream):
                        new_photo_name = md5(str(User.id).encode()).hexdigest()
                        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], new_photo_name))
                        new_user_data['profile_picture'] = "avatars/"+new_photo_name
                    else:
                        return render_template(
                            "users/change-profile.html", user=user, error="Only images are allowed"
                        )
                else:
                    return render_template(
                        "users/change-profile.html", user=user, error="Photo is too large"
                    )

        if new_user_data:
            user.edit(new_user_data)
            return redirect(url_for("user_page"))
        else:
            return render_template(
                "users/change-profile.html", user=user, error="user data has not changed"
            )


@app.route('/news/<int:news_id>')
@auth_required
def news_page(news_id):
    news = News(news_id)
    news_data = news.get()
    return render_template('news.html', news=news_data)


@app.route('/')
@auth_required
def index():
    return render_template('index.html', newsList=get_news())
