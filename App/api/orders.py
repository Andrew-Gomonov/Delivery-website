from App.errors.api import APIBadRequestError, APINotFoundError
from App import conn, cur, app


def get_last_order_id():
    cur.execute("SELECT id FROM Orders")
    ids = cur.fetchall()
    if not ids:
        return 1
    else:
        return ids[-1][0]


def get_orders():
    json_data = []
    cur.execute(
        "SELECT * FROM Orders"
    )
    data = cur.fetchall()
    for item in data:
        json_data.append({
            "order_id": item[0],
            'customer_name': item[1],
            'customer_phone': item[2],
            'customer_address': item[3],
            'courier_id': item[4],
            "date_placed": item[5],
            'status': item[6],
            'total_price': item[7],
            'deliver_time': item[8],
            'products': get_products(item[0])
        })
    return json_data


def get_products(order_id):
    cur.execute(
        "SELECT  Products.name,Products.price,Products.vendor_code,Products.description,Products.image,"
        " Order_items.quantity "
        "FROM Orders "
        "JOIN Order_items ON Order_items.order_id = Orders.id "
        "JOIN Products ON Order_items.product_id = Products.id "
        f"WHERE Orders.id = '{order_id}'"
    )
    data = cur.fetchall()
    return data


def get_products_lists_from_form(request_form):
    vendor_codes = []
    orders_quantity = []
    for item in request_form.lists():
        if item[0] == 'order_vendor_code':
            vendor_codes = item[1]
        elif item[0] == 'order_quantity':
            orders_quantity = item[1]
    if len(vendor_codes) != len(orders_quantity):
        raise APIBadRequestError('Product(s) lacks a supplier code or quantity of product')
    return vendor_codes, orders_quantity


def get_products_from_lists(products_lists):
    return zip(products_lists[0], products_lists[1])


def get_product_by_vendor_code(vendor_code):
    cur.execute(f"SELECT * FROM Products WHERE vendor_code='{vendor_code}'")
    product = cur.fetchone()
    if not product:
        raise APINotFoundError(f'Product with vendor code {vendor_code} not found')
    return product


def create_order(data_order):
    customer_name = data_order['customer_name']
    phone_number = data_order['order_phone_number']
    customer_address = data_order['order_address']
    deliver_time = data_order['order_deliver_time']
    if not customer_name:
        raise APIBadRequestError('No customer name')
    if not phone_number:
        raise APIBadRequestError('No phone number')
    if not customer_address:
        raise APIBadRequestError('No customer address')
    order_total = 0.0
    for vendor_code in get_products_lists_from_form(data_order)[0]:
        order_total += float(get_product_by_vendor_code(vendor_code)[2])
    order_total = order_total + app.config['DELIVERY_MONEY']
    cur.execute(
        "INSERT INTO Orders "
        "(customer_name,customer_phone,customer_adress,date_placed,order_total,customer_deliver_time)"
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
