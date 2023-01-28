import bcrypt
from flask import current_app
from datetime import datetime
from App import cur, conn
from App.core.orders import (
    get_order_products, get_products_from_lists, get_products_lists_from_form,
    get_product_by_vendor_code,
)
from App.core.products import products_changed
from App.errors.api import APINotFoundError, APIBadRequestError


class Product:
    def __init__(self, order_item_id, quantity, name, price, vendor_code, description, photo):
        self.order_item_id = order_item_id
        self.quantity = quantity
        self.name = name
        self.price = price
        self.vendor_code = vendor_code
        self.description = description
        self.photo = photo

    def __repr__(self):
        return f'<Product {self.name}>'


class Customer:
    def __init__(self, name, phone, address):
        self.name = name
        self.phone = phone
        self.address = address

    def __repr__(self):
        return f'<Customer {self.name}>'


class Order:
    def __init__(self, order_id: int):
        cur.execute(f"select * from Orders where id='{order_id}'")
        info = cur.fetchone()
        if info is None:
            raise APINotFoundError("Order not found in database")
        self.id: int = info[0]
        self.customer = Customer(info[1], info[2], info[3])
        self.courier_id = info[4]
        self.datetime: str = str(info[5])
        self.status: str = info[6]
        self.total_price: float = info[7]
        self.deliver_time: str = info[8]
        self.products: list[Product] = []
        for product in get_order_products(order_id):
            self.products.append(
                Product(product[6], product[5], product[0], product[1], product[2], product[3], product[4]))

    def edit(self, data_to_edit):
        form_data = {k: v for k, v in data_to_edit.items() if
                     k in ['product_vendor_code', 'product_quantity', 'order_customer_name', 'order_phone_number',
                           'order_address', 'order_deliver_time', 'order_total_price']}

        customer_name = form_data.get('order_customer_name')
        customer_phone_number = form_data.get('order_phone_number')
        order_address = form_data.get('order_address')
        order_total_price = float(form_data.get('order_total_price'))
        form_products = list(get_products_from_lists(get_products_lists_from_form(data_to_edit)))
        deliver_time = form_data.get('order_deliver_time')
        is_products_changed = products_changed(form_products, self.products)
        order_total = 0.0
        if order_total_price != self.total_price:
            order_total = order_total_price
        elif order_total_price != self.total_price and is_products_changed:
            order_total = order_total_price
        elif is_products_changed:
            for product in form_products:
                order_total += int(get_product_by_vendor_code(product[0])['price']) * int(product[1])
            order_total += current_app.config['DELIVERY_MONEY']
            # delete all existing products associated with this order
            cur.execute(f"DELETE FROM Order_items WHERE order_id={self.id}")
            conn.commit()

            # add new products to the Order_Items table
            for product in form_products:
                cur.execute(
                    "INSERT INTO Order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (self.id, get_product_by_vendor_code(product[0])['id'], product[1]))
            conn.commit()
        else:
            order_total = self.total_price
        if customer_name == self.customer.name \
                and order_address == self.customer.address and customer_phone_number == self.customer.phone \
                and order_total == self.total_price and deliver_time == self.deliver_time and not is_products_changed:
            raise APIBadRequestError("Order don't changed")
        else:
            cur.execute(
                "UPDATE Orders SET customer_name = %s, "
                "customer_phone = %s, order_total = %s, "
                "customer_address = %s, customer_deliver_time = %s WHERE id = %s",
                (customer_name, customer_phone_number, order_total, order_address, deliver_time, self.id))
            conn.commit()
        return True

    def to_dict(self):
        """
        Get order in dict
        :return: dictionary that contain id,title,content,publish_date,image
        """
        return self.__dict__

    def delete(self):
        cur.execute(f"DELETE FROM Order_items WHERE order_id='{self.id}'")
        cur.execute(f"DELETE FROM Orders WHERE id='{self.id}'")
        conn.commit()
        return True

    def __repr__(self):
        return f'<Order {self.id}>'


class News:
    def __init__(self, news_id: int):
        cur.execute(f"select * from News where id='{news_id}'")
        info = cur.fetchone()
        if info is None:
            raise APINotFoundError("News not found in database")
        self.id: int = news_id
        self.title: str = info[1]
        self.content: str = info[2]
        self.image: str = info[3]
        self.author: str = info[4]
        self.datetime = str(info[5])

    def to_dict(self):
        """
        Get news in dict
        :return: dictionary that contain id,title,content,publish_date,image
        """
        return self.__dict__

    def delete(self) -> bool:
        """
        Delete news by id
        :return: code and message
        """
        cur.execute(f"DELETE FROM News WHERE id='{self.id}'")
        conn.commit()
        return True

    def edit(self, data_to_edit: dict) -> bool:
        """
        Edit news by dictionary
        :param data_to_edit: this is a dictionary in which there should be data to change
        :return: code and message
        """
        for key in data_to_edit.keys():
            if key not in self.__dict__.keys():
                raise APIBadRequestError("Unknown key in  news dictionary")
        result = ""
        for key, value in data_to_edit.items():
            result += f"{key} = '{value}',"
        result = result[:-1]
        # Updating database
        cur.execute(f"UPDATE News SET {result} WHERE id='{self.id}'")
        # Updating object
        self.__dict__.update(data_to_edit)
        return True

    def __repr__(self):
        return f'<News {self.id}>'


class User:
    """
    User crud(crud - create, read, update, delete)
    """
    # Constructor
    def __init__(self, user_id: int = None, info: list = None):
        if info is None:
            cur.execute(f"select * from Users where id='{user_id}'")
            info = cur.fetchone()
            if info is None:
                raise APINotFoundError("User not found in database")
        if user_id is not None:
            self.id: int = user_id
        else:
            self.id: int = info[0]
        self.name: str = info[1]
        self.password: str = info[2]
        self.email: str = info[3]
        self.register_datetime: datetime = info[4]
        self.is_admin: int = info[5]
        self.profile_picture: str = info[6]
        self.phone: str = info[7]

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        """
        Get user information in dict
        :return: dictionary that contain id,name,email,
        password,registration date,is admin(1 - yes,0 - no),profile_picture
        """
        return self.__dict__

    def delete(self) -> bool:
        """
        Delete user by id
        :return: code and message
        """
        cur.execute(f"DELETE FROM Users WHERE id='{self.id}'")
        conn.commit()
        return True

    def edit(self, data_to_edit: dict) -> bool:
        """
        Edit user by dictionary
        :param data_to_edit: this is a dictionary in which there should be data to change
        :return: code and message
        """
        for key in data_to_edit.keys():
            if key not in self.__dict__.keys():
                raise APIBadRequestError("Unknown key in  user dictionary")
        if 'password' in data_to_edit.keys():
            data_to_edit['password'] = bcrypt.hashpw(data_to_edit['password'].encode(), bcrypt.gensalt()).decode()
        result = ""
        for key, value in data_to_edit.items():
            result += f"{key} = '{value}',"
        result = result[:-1]
        # Updating database
        cur.execute(f"UPDATE Users SET {result} WHERE id='{self.id}'")
        conn.commit()
        # Updating object
        self.__dict__.update(data_to_edit)
        return True
