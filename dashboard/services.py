from django.db import connection
from contextlib import closing

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns,row)) for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns,row))

def get_order_by_user(id):
    with closing(connection.cursor()) as cursor:
        cursor.execute(""" SELECT products_order.id, products_customer.first_name,products_customer.last_name, products_order.address, products_order.payment_type,products_order.status,products_order.created_at from products_order 
                            INNER JOIN products_customer on products_customer.id=products_order.customer_id 
                            where products_order.customer_id =%s""",[id])
        order = dictfetchall(cursor)
        return order

def get_product_by_order(id):
    with closing(connection.cursor()) as cursor:
        cursor.execute(""" SELECT products_orderproduct.count,products_orderproduct.price,
        products_orderproduct.created_at,products_product.title from products_orderproduct 
         INNER JOIN products_product ON products_orderproduct.product_id=products_product.id  where order_id=%s""",[id])
        orderproduct = dictfetchall(cursor)
        return orderproduct

def get_table():
    with closing(connection.cursor()) as cursor:
        cursor.execute(""" 
        SELECT products_orderproduct.product_id, 
COUNT(products_orderproduct.product_id),products_product.title 
FROM products_orderproduct 
INNER JOIN products_product ON products_product.id=products_orderproduct.product_id 
GROUP BY products_orderproduct.product_id ,products_product.title 
order by count desc limit 10

        """)
        table = dictfetchall(cursor)
        return table