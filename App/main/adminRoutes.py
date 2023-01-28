from flask import render_template, request, redirect, url_for, current_app, send_from_directory
from App.core.decorators import only_admins, auth_required
from App.core.models import User, Order
from App.core.orders import create_orders_file, delete_order, create_order
from App.core.products import get_product_by_id, create_product, \
    delete_product, get_products, validate_product_data, update_product, get_total_pages
from App.core.users import create_user, get_next_last_user_id, validate_user_data, get_users
from App.core.utils import LOG, upload_photo
from App.errors.api import APIBadRequestError, APINotFoundError
from App.main import bp


@bp.route('/create-user', methods=['GET', 'POST'])
@auth_required
@only_admins
def create_user_page():
    if request.method == "GET":
        return render_template('admins/create-user.html')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        form_is_admin = request.form.get('is_admin')
        if not all([name, email, password, password_confirm, phone]):
            return render_template('admins/create-user.html', error='User information is incomplete')
        if password != password_confirm:
            return render_template('admins/create-user.html', error='Passwords do not match')
        if form_is_admin is None:
            is_admin = 0
        else:
            is_admin = 1
        try:
            path_profile_picture = upload_photo(request, get_next_last_user_id(), "avatars")
        except APIBadRequestError as err:
            return render_template('admins/create-user.html', error=err)
        try:
            create_user(
                {
                    "email": email,
                    "name": name,
                    "password": password,
                    "is_admin": is_admin,
                    "profile_picture": path_profile_picture,
                    "phone": phone
                }
            )
        except APIBadRequestError as err:
            return render_template('admins/create-user.html', error=err)
        return redirect(url_for("main.users_page"))


@bp.route('/update-product', methods=['GET', 'POST'])
@auth_required
@only_admins
def admin_update_product():
    product_id = request.args.get('product_id', None, int)
    product = get_product_by_id(product_id)
    if request.method == "GET":
        return render_template('admins/change-product.html', product=product)
    else:
        try:
            data = validate_product_data(request, product)
            update_product(data)
        except APIBadRequestError as err:
            return render_template('admins/change-product.html', product=product, error=err)
        return redirect(url_for("main.products_page"))


@bp.route('/create-product', methods=['GET', 'POST'])
@auth_required
@only_admins
def admin_create_product():
    if request.method == "GET":
        return render_template('admins/create-product.html')
    else:
        name = request.form.get('name')
        vendor_code = request.form.get('vendorCode')
        description = request.form.get('description')
        price = request.form.get('price')
        if not all([name, vendor_code, description, price]):
            return render_template('admins/create-product.html', error="Product information is incomplete")
        try:
            path_product_picture = upload_photo(request, get_next_last_user_id(), "products")
        except APIBadRequestError as err:
            return render_template('admins/create-product.html', error=err)
        try:
            create_product({
                'name': name,
                'price': price,
                'vendor_code': vendor_code,
                'description': description,
                'image': path_product_picture
            })
        except APIBadRequestError as err:
            return render_template('admins/create-product.html', error=err)
        return redirect(url_for('main.products_page'))


@bp.route('/delete-user')
@auth_required
@only_admins
def admin_delete_user():
    user_id = abs(request.args.get('user_id', None, type=int))
    if user_id is not None:
        user = User(user_id)
        user.delete()
        return redirect(url_for('main.users_page'))
    else:
        return redirect(url_for('main.users_page'))


@bp.route('/delete-product')
@auth_required
@only_admins
def admin_delete_product():
    product_id = abs(request.args.get('product_id', None, type=int))
    if product_id is not None:
        delete_product(product_id)
        return redirect(url_for('main.products_page'))
    else:
        return redirect(url_for('main.products_page'))


@bp.route('/products')
@auth_required
@only_admins
def products_page():
    page = abs(request.args.get('page', 1, type=int))
    per_page = int(current_app.config['PER_PAGE'])
    products = get_products(page, per_page)
    total_pages = get_total_pages(per_page)
    return render_template(
        "admins/products.html",
        products=products,
        total_pages=total_pages,
        last_page=total_pages + 1,
        current_page=page
    )


@bp.route('/export-as-csv')
@auth_required
@only_admins
def export_table_as_csv():
    page = request.args.get('page', None, type=int)
    if page is None:
        create_orders_file()
    else:
        create_orders_file(page=abs(page), per_page=current_app.config['PER_PAGE'])
    return send_from_directory(directory="static/csv", path="orders.csv")


@bp.route('/edit-user', methods=['GET', 'POST'])
@auth_required
@only_admins
def admin_edit_user_profile():
    user_id = request.args.get('user_id', None, type=int)
    if user_id is not None:
        user = User(user_id)
        if request.method == "GET":
            return render_template(
                'admins/change-user-profile.html',
                profile_user=user.to_dict(),
                current_user_id=user_id
            )
        else:
            try:
                data = validate_user_data(request, user, True)
                user.edit(data)
            except APIBadRequestError as err:
                return render_template(
                    'admins/change-user-profile.html',
                    profile_user=user,
                    error=err,
                    current_user_id=user_id
                )
            return redirect(url_for('main.users_page'))
    else:
        return redirect(url_for('main.users_page'))


@bp.route('/users')
@auth_required
@only_admins
def users_page():
    page = abs(request.args.get('page', 1, type=int))
    per_page = int(current_app.config['PER_PAGE'])
    users = get_users(page, per_page)
    total_pages = get_total_pages(per_page)
    return render_template(
        'admins/users.html',
        users=users,
        total_pages=total_pages,
        last_page=total_pages + 1,
        current_page=page
    )


@bp.route('/delete-order')
@auth_required
@only_admins
def delete_order_page():
    order_id = abs(request.args.get('order', 1, type=int))
    delete_order(order_id)
    return redirect(url_for('main.orders_page'))


@bp.route('/edit-order', methods=['GET', 'POST'])
@auth_required
@only_admins
def edit_order():
    order_id = abs(request.args.get('order', 1, type=int))
    order = Order(order_id)
    if request.method == "POST":
        try:
            order.edit(request.form)
        except APIBadRequestError as err:
            return render_template('admins/edit-order.html', order=order, error=str(err))
        except APINotFoundError as err:
            return render_template('admins/edit-order.html', order=order, not_found=err)
        return redirect(url_for('main.orders_page'))
    else:
        return render_template('admins/edit-order.html', order=order)


@bp.route('/create-new-order', methods=['GET', 'POST'])
@auth_required
@only_admins
def create_new_order():
    if request.method == 'POST':
        try:
            create_order(request.form)
        except APIBadRequestError as error:
            return render_template(
                "admins/create-new-order.html",
                error=error
            )
        except APINotFoundError as error:
            return render_template(
                "admins/create-new-order.html",
                not_found=error
            )
        LOG.info(f"User {request.remote_addr} created order")
        return redirect(url_for("main.orders_page"))
    else:
        return render_template("admins/create-new-order.html")
