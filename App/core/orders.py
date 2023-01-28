import csv
import math
import os
from flask import current_app
from App import conn, cur
from App.core.products import get_order_products, get_products_from_lists, get_products_lists_from_form, \
    get_product_by_vendor_code
from App.errors.api import APIBadRequestError, APINotFoundError


def get_last_order_id():
    cur.execute("SELECT MAX(id) FROM Orders")
    max_id = cur.fetchone()
    if not max_id:
        return 1
    else:
        return max_id[0]


def create_orders_file(path="App/static/csv/", page=None, per_page=None):
    if not os.path.exists('App/static/csv'):
        os.mkdir('App/static/csv')
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM Orders ORDER BY date_placed DESC LIMIT %s OFFSET %s", (per_page, offset))
    else:
        cur.execute("SELECT * FROM Orders")
    orders = cur.fetchall()
    field_names = [i[0] for i in cur.description]
    field_names.append('products')
    with open(path+"orders.csv", "w") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(field_names)
        for order in orders:
            products = get_order_products(order[0])
            str_products = ""
            for product in products:
                str_products += f"{product[2]}({product[5]}) "
            order = list(order)
            order.append(str_products)
            writer.writerow(
                [
                    order[0],
                    order[1],
                    order[2],
                    order[3],
                    get_courier_name_by_id(order[4]),
                    order[5],
                    order[6],
                    order[7],
                    order[8],
                    order[9],
                    str_products
                ]
            )


def get_courier_name_by_id(courier_id):
    cur.execute("SELECT name FROM Users WHERE id=%s", (courier_id,))
    courier_name = cur.fetchone()
    if courier_name:
        courier_name = courier_name[0]
    return courier_name


def delete_order(order_id):
    cur.execute(f"DELETE FROM Order_items WHERE order_id='{order_id}'")
    cur.execute(f"DELETE FROM Orders WHERE id='{order_id}'")
    conn.commit()
    return True


def start_order(courier_id, order_id):
    cur.execute("UPDATE Orders SET `status` = 'In progress', `courier_id`=%s WHERE id=%s", (courier_id, order_id))
    conn.commit()
    return True


def comment_order(order_id, comment):
    cur.execute("UPDATE Orders SET comment = %s WHERE id=%s", (comment, order_id))
    conn.commit()
    return True


def end_order(order_id):
    cur.execute("UPDATE Orders SET status = 'Done' WHERE id=%s", (order_id,))
    conn.commit()
    return True


def get_total_pages(per_page):
    cur.execute("SELECT COUNT(*) FROM Orders")
    total_rows = cur.fetchone()[0]
    return math.ceil(total_rows / per_page)


def get_orders(page=None, per_page=None) -> list[dict]:
    """
    Returns the order list.
    If page and per_page parameters are not specified it returns all orders or only the specified page
    """
    json_data = []
    if page and per_page:
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM Orders ORDER BY date_placed DESC LIMIT %s OFFSET %s", (per_page, offset))
    else:
        cur.execute("SELECT * FROM Orders")
    data = cur.fetchall()
    for item in data:
        json_data.append({
            "order_id": item[0],
            'customer_name': item[1],
            'customer_phone': item[2],
            'customer_address': item[3],
            'courier_id': item[4],
            'courier_name': get_courier_name_by_id(item[4]),
            "date_placed": item[5],
            'status': item[6],
            'total_price': item[7],
            'deliver_time': item[8],
            'products': get_order_products(item[0]),
            'comment': item[9]
        })
    return json_data


def create_order(data_order) -> bool:
    customer_name = data_order.get('order_customer_name')
    phone_number = data_order.get('order_phone_number')
    customer_address = data_order.get('order_address')
    deliver_time = data_order.get('order_deliver_time')
    if not customer_name:
        raise APIBadRequestError('No customer name')
    if not phone_number:
        raise APIBadRequestError('No phone number')
    if not customer_address:
        raise APIBadRequestError('No customer address')
    order_total = 0.0
    products = get_products_from_lists(get_products_lists_from_form(data_order))
    for product in products:
        order_total += int(get_product_by_vendor_code(product[0])[2]) * int(product[1])
    order_total = order_total + current_app.config['DELIVERY_MONEY']
    cur.execute(
        "INSERT INTO Orders "
        "(customer_name,customer_phone,customer_address,date_placed,order_total,customer_deliver_time)"
        f" VALUES ('{customer_name}', '{phone_number}', '{customer_address}', "
        f"CURRENT_TIMESTAMP, '{order_total}','{deliver_time}')"
    )
    conn.commit()
    create_order_products(data_order)
    return True


def create_order_products(data_order):
    products_sql = ""
    next_order_id = get_last_order_id()
    for product in get_products_from_lists(get_products_lists_from_form(data_order)):
        products_sql += f"({next_order_id},{get_product_by_vendor_code(product[0])[0]},'{product[1]}'),"
    products_sql = products_sql[:-1]
    cur.execute(
        f"INSERT INTO Order_items (order_id,product_id,quantity) VALUES {products_sql}"
    )
    conn.commit()
    return True
