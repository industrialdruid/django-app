from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order
from django.contrib.auth.models import User


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file, restkey="products")
    proceeded = list()
    for row in reader:
        proceeded_row = dict()
        for key, value in row.items():
            if key == "user":
                user = User.objects.get(username=value)
                proceeded_row[key] = user
            elif key != "products":
                proceeded_row[key] = value
        if len(proceeded_row) != 0:
            proceeded.append(proceeded_row)

    orders = [Order(**row) for row in proceeded]

    csv_file.seek(0)
    for index, row in enumerate(reader):
        for key, value in row.items():
            if key == "products":
                products = list()
                for product_name in value:
                    products.append(Product.objects.get(name=product_name))
                proceeded[index-1][key] = products

    orders_old_pks = [order.pk for order in orders]
    for order in orders:
        order.save()
    new_orders = [order for order in orders if order.pk not in orders_old_pks]
    print(new_orders)

    for index, order in enumerate(new_orders):
        order.products.set(proceeded[index]["products"])

    return orders
