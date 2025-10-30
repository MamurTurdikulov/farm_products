from django.db import connection
from contextlib import closing

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a list of dicts.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """
    Return a single row from a cursor as a dict.
    """
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def get_product_by_id(product_id: int):
    """
    Retrieve a product record by its ID.
    """
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            """SELECT * FROM products_product WHERE id = %s""",
            [product_id]
        )
        product = dictfetchone(cursor)
        return product


def get_orderproduct_by_id(orderproduct_id: int):
    """
    Retrieve an order-product (junction table) record by its ID.
    """
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            """SELECT * FROM products_orderproduct WHERE id = %s""",
            [orderproduct_id]
        )
        order_product = dictfetchone(cursor)
        return order_product


def get_user_by_phone(phone_number: str):
    """
    Retrieve a customer record by phone number.
    """
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            """SELECT * FROM products_customer WHERE phone_number = %s""",
            [phone_number]
        )
        user = dictfetchone(cursor)
        return user