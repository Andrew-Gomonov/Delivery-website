import math
import os
from hashlib import md5
from flask import current_app
from werkzeug.utils import secure_filename
from App import cur, conn
from App.core.utils import validate_image
from App.errors.api import APINotFoundError, APIBadRequestError


def validate_product_data(request, product):
    new_product_data = {}
    name = request.form.get('name')
    description = request.form.get('description')
    vendor_code = request.form.get('vendorCode')
    price = request.form.get('price')

    if name != product['name']:
        new_product_data['name'] = name
    if description != product['description']:
        new_product_data['description'] = description
    if vendor_code != product['vendor_code']:
        new_product_data['vendor_code'] = vendor_code
    if price != product['price']:
        new_product_data['price'] = price

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
                    new_photo_name = md5(str(product['id']).encode()).hexdigest()
                    photo.save(os.path.join('App/static/products', new_photo_name))
                    new_product_data['image'] = "products/" + new_photo_name
                else:
                    raise APIBadRequestError("Only images are allowed")
            else:
                return APIBadRequestError("Photo is too large")
    if not new_product_data:
        raise APIBadRequestError("product data has not changed")
    new_product_data['id'] = product['id']
    return new_product_data


def get_product_by_id(product_id) -> dict:
    cur.execute("SELECT * FROM Products WHERE id=%s", (product_id,))
    product = cur.fetchone()
    if not product:
        raise APINotFoundError(f'Product with id {product_id} not found')
    product_dict = {
        "id": product[0],
        "name": product[1],
        "price": product[2],
        "vendor_code": product[3],
        "description": product[4],
        "image": product[5]
    }
    return product_dict


def products_changed(form_products, products):
    is_products_changed = False
    for form_product in form_products:
        for product in products:
            if form_product[0] != product.vendor_code or form_product[1] != product.quantity:
                is_products_changed = True
    return is_products_changed


def delete_product(product_id):
    cur.execute(f"DELETE FROM Products WHERE id = {product_id}")
    cur.commit()
    return True


def update_product(product_data: dict):
    for key in product_data.keys():
        if key not in ['name', 'price', 'vendor_code', 'description', 'image', 'id']:
            raise APIBadRequestError("Unknown key in product dictionary")
    result = ""
    for key, value in product_data.items():
        result += f"{key} = '{value}',"
    result = result[:-1]
    # Updating database
    cur.execute(f"UPDATE Products SET {result} WHERE id='{product_data['id']}'")
    conn.commit()
    return True


def create_product(product_data: dict):
    for key in product_data.keys():
        if key not in ['name', 'price', 'vendor_code', 'description', 'image']:
            raise APIBadRequestError("Unknown key in product dictionary")
    cur.execute(f"SELECT id FROM Products WHERE vendor_code='{product_data['vendor_code']}'")
    product = cur.fetchone()
    if product is not None:
        raise APIBadRequestError("A product with this vendor_code already exists")
    cur.execute(
        "INSERT INTO Products(name, price, vendor_code, description, image) VALUES (%s,%s,%s,%s,%s)",
        (
            product_data['name'],
            product_data['price'],
            product_data['vendor_code'],
            product_data['description'],
            product_data['image']
         )
    )
    conn.commit()
    return True


def get_total_pages(per_page):
    cur.execute("SELECT COUNT(*) FROM Products")
    total_rows = cur.fetchone()[0]
    return math.ceil(total_rows / per_page)


def get_products(page, per_page):
    if page and per_page:
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM Products ORDER BY name LIMIT %s OFFSET %s", (per_page, offset))
    else:
        cur.execute("SELECT * FROM Products")
    products = cur.fetchall()
    return products


def get_order_products(order_id) -> list:
    cur.execute(
        "SELECT  Products.name,Products.price,Products.vendor_code,Products.description,Products.image,"
        " Order_items.quantity, Order_items.id,Products.id "
        "FROM Orders "
        "JOIN Order_items ON Order_items.order_id = Orders.id "
        "JOIN Products ON Order_items.product_id = Products.id "
        f"WHERE Orders.id = '{order_id}'"
    )
    data = cur.fetchall()
    return data


def get_products_lists_from_form(request_form):
    vendor_codes = []
    products_quantity = []
    for item in request_form.lists():
        if item[0] == 'product_vendor_code':
            if "" not in item[1]:
                vendor_codes = item[1]
        elif item[0] == 'product_quantity':
            if "" not in item[1]:
                products_quantity = item[1]
    if len(vendor_codes) == 0 and len(vendor_codes) == 0:
        raise APIBadRequestError('There are no products')
    if len(vendor_codes) != len(products_quantity):
        raise APIBadRequestError('Product(s) lacks a supplier code or/and quantity of product')
    return vendor_codes, products_quantity


def get_products_from_lists(products_lists):
    return zip(products_lists[0], products_lists[1])


def get_product_by_vendor_code(vendor_code) -> dict:
    cur.execute(f"SELECT * FROM Products WHERE vendor_code='{vendor_code}'")
    product = cur.fetchone()
    if not product:
        raise APINotFoundError(f'Product with vendor code {vendor_code} not found')
    product_dict = {
        "name": product[1],
        "id": product[0],
        "price": product[2],
        "vendor_code": product[3],
        "description": product[4],
        "image": product[5]
    }
    return product_dict
