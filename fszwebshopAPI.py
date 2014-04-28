from flask import Flask, Response
import web
import sql
import simplejson as json

import simplejson as json
app = Flask(__name__)
app.config.from_object('config')
app.config.items()

app.test_request_context()

mysqlcon = sql.db_conn(app)
data = mysqlcon.get_customers()
mycucustomers = web.customers(mysqlcon)

print(data)

@app.route('/get/customer', methods=['GET'])
def get_customers():
    print('---------')
    mycucustomers.set_no_filter()
    return Response(json.dumps(mycucustomers.customers),mimetype='application/json')


@app.route('/get/categories', methods=['GET'])
def get_categories():
    print('---------')
    mycategories = web.categories(mysqlcon)
    return Response(json.dumps(mycategories.get_top_categories()),mimetype='application/json')
@app.route('/get/sub_category_<cat_id>.json', methods=['GET','POST'])
def get_sub_categories_product(cat_id):
    print(cat_id)
    category_id = int(cat_id)
    print(category_id)
    mycategories = web.categories(mysqlcon)
    products = mycategories.get_sub_categories_to_top(category_id)
    return Response(json.dumps(products),mimetype='application/json')

@app.route('/get/products_by_cat_id_<cat_id>', methods=['GET','POST'])
def get_product_by_cat_id(cat_id):
    print(cat_id)
    category_id = int(cat_id)
    print(category_id)
    mycategories = web.categories(mysqlcon)
    products = mycategories.get_products_by_category(category_id)
    return Response(json.dumps(products, use_decimal=True),mimetype='application/json')

@app.route('/get/product_by_id_<product_id>', methods=['GET','POST'])
def get_product_cat_id(product_id):
    print(product_id)
    product_id = int(product_id)

    print(product_id)
    current_product = web.product(product_id, mysqlcon)
    current_product.product['date_added'] = ''
    current_product.product['date_available'] = ''
    current_product.product['date_modified'] = ''
    current_product.product['price'] = ''
    return Response(json.dumps(current_product.product, use_decimal=True),mimetype='application/json')


@app.route('/')
def hello_world():
    return 'bla'


if __name__ == '__main__':

    app.run(host='0.0.0.0')
