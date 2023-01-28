from App.api import bp
from flask import request, jsonify
from App.core.models import News, User
from App.core.news import get_news, create_news
from App.core.users import get_users, create_user
from App.core.tokens import dev_token_required


@bp.route('/api/news', methods=['GET', 'POST'])
@dev_token_required
def news_api_page():
    if request.method == 'GET':
        data = get_news()
    else:
        create_news(request.form)
        data = {
            "code": 200,
            "message": "News created"
        }

    return jsonify(data)


@bp.route('/api/news/<int:news_id>', methods=['GET', 'DELETE', 'PUT'])
@dev_token_required
def news_api_crud_page(news_id):
    news = News(news_id)
    data = {
        "code": 200
    }
    if request.method == 'GET':
        data = news.to_dict()
    elif request.method == "PUT":
        news.edit(request.form)
        data['message'] = "News updated"
    else:
        news.delete()
        data['message'] = "News deleted"
    return jsonify(data)


@bp.route('/api/users', methods=['GET', 'POST'])
@dev_token_required
def users_api_page():
    if request.method == 'GET':
        data = get_users()
    else:
        create_user(request.form)
        data = {
            "code": 200,
            "message": "User created"
        }

    return jsonify(data)


@bp.route('/api/users/<int:user_id>', methods=['GET', 'DELETE', 'PUT'])
@dev_token_required
def user_api_page(user_id):
    user = User(user_id)
    data = {
        "code": 200
    }
    if request.method == 'GET':
        data = user.to_dict()
    elif request.method == "PUT":
        user.edit(request.form)
        data['message'] = "User updated"
    else:
        user.delete()
        data['message'] = "User deleted"
    return jsonify(data)