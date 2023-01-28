import secrets
import jwt
from urllib.parse import urlparse
from App.main import bp
from App.core.news import get_news
from App.core.models import User, News
from App.core.decorators import auth_required
from App.core.users import login, is_authenticated, get_delivery_history, validate_user_data
from App.core.utils import LOG
from App.core.orders import get_orders, get_total_pages, start_order, end_order, comment_order
from App.core.products import get_product_by_id
from App.errors.api import APIAuthError, APIBadRequestError, APINotFoundError
from flask import render_template, request, redirect, url_for, current_app, session


@bp.app_context_processor
def inject_data():
    if session.get('token'):
        try:
            user = User(jwt.decode(session.get('token'), current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub'])
        except jwt.exceptions.InvalidTokenError:
            user = None
    else:
        user = None
    return dict(
        company_name=current_app.config['COMPANY_NAME'],
        company_site=current_app.config['COMPANY_SITE'],
        company_emails=current_app.config['COMPANY_EMAILS'],
        company_numbers=current_app.config['COMPANY_NUMBERS'],
        company_description=current_app.config['COMPANY_DESCRIPTION'],
        company_address=current_app.config['COMPANY_ADDRESS'],
        company_social_networks=current_app.config['SOCIAL_NETWORKS'],
        user=user
    )


@bp.route('/product')
@auth_required
def product_page():
    product_id = request.args.get('product_id', None, type=int)
    try:
        product = get_product_by_id(product_id)
        return render_template("product.html", product=product)
    except APINotFoundError:
        return redirect(url_for('main.orders_page'))


@bp.route('/profile')
@auth_required
def profile():
    user_id = jwt.decode(session.get('token'), current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    delivery_history = get_delivery_history(user_id)
    return render_template("users/profile.html", delivery_history=delivery_history)


@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        try:
            auth_token = login(request.form)
            LOG.info(f"User {request.remote_addr} sign in")
            session['token'] = auth_token
            return redirect(url_for('main.index'))
        except APIAuthError as error:
            return render_template('users/login.html', error=error.message)
    else:
        if is_authenticated() is True:
            return redirect(url_for("main.index"))
        session['csrf_token'] = secrets.token_urlsafe()
        return render_template('users/login.html')


@bp.route('/start-order')
@auth_required
def start_order_page():
    order_id = abs(request.args.get('order', 1, type=int))
    user_id = jwt.decode(session.get('token'), current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    start_order(user_id, order_id)
    return redirect(url_for("main.orders_page"))


@bp.route('/end-order')
@auth_required
def end_order_page():
    order_id = abs(request.args.get('order', 1, type=int))
    end_order(order_id)
    return redirect(url_for("main.orders_page"))


@bp.route('/comment-order', methods=['POST'])
@auth_required
def comment_order_page():
    order_id = request.form.get('order_id')
    comment = request.form.get('comment')
    comment_order(order_id, comment)
    return redirect(url_for("main.orders_page"))


@bp.route('/orders')
@auth_required
def orders_page():
    LOG.info(f"User {request.remote_addr} get orders page")
    # Pagination orders
    page = abs(request.args.get('page', 1, type=int))
    per_page = int(current_app.config['PER_PAGE'])
    total_pages = get_total_pages(per_page)
    orders = get_orders(page, per_page)
    return render_template(
        "orders.html",
        orders=orders,
        total_pages=total_pages,
        last_page=total_pages+1,
        current_page=page
    )


@bp.route('/chat')
@auth_required
def chat_page():
    LOG.info(f"User {request.remote_addr} get chat page")
    return render_template("users/chat.html")


@bp.route('/search')
@auth_required
def search_page():
    LOG.info(f"User {request.remote_addr} get search page")
    query = request.args.get('query')
    referrer_url = request.referrer
    if not query:
        return render_template("search.html", error='no query')
    if not referrer_url == '':
        return render_template("search.html", error='no page')
    parsed_referrer_url = urlparse(referrer_url)
    if parsed_referrer_url.path == '':
        return render_template("search.html", error='no page')
    return render_template("search.html")


@bp.route('/edit-profile', methods=['GET', 'POST'])
@auth_required
def edit_profile():
    user_id = jwt.decode(session.get('token'), current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
    user = User(user_id)
    if request.method == "GET":
        LOG.info(f"User {request.remote_addr} get change profile page")
        return render_template("users/change-profile.html", user=user)
    else:
        try:
            data = validate_user_data(request, user)
            user.edit(data)
        except APIBadRequestError as err:
            return render_template('users/change-profile.html', error=err)
        return redirect(url_for("main.index"))


@bp.route('/news/<int:news_id>')
@auth_required
def news_page(news_id):
    news = News(news_id)
    LOG.info(f"User {request.remote_addr} read news with id {news.id}")
    return render_template('news.html', news=news)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("main.login_page"))


@bp.route('/')
@auth_required
def index():
    LOG.info(f"User {request.remote_addr} get main page")
    return render_template('index.html', newsList=get_news(), page='index')
