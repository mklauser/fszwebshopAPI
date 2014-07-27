import simplejson as json

from flask import Flask, Response, url_for

import web
import sql


app = Flask(__name__)
app.config.from_object('config')
app.config.items()

app.test_request_context()

mysqlcon = sql.db_conn(app)
data = mysqlcon.get_customers()
mycucustomers = web.customers(mysqlcon)


@app.route('/get/customer', methods=['GET'])
def get_customers():
    """
    Get all available customers from the OC DB.
    :return: single json.
    """
    mycucustomers.set_no_filter()
    return Response(json.dumps(mycucustomers.customers), mimetype='application/json')


@app.route('/get/categories', methods=['GET'])
def get_categories():
    """
    Get all available categories from the OC DB.
    :return: single json.
    """
    mycategories = web.categories(mysqlcon)
    return Response(json.dumps(mycategories.get_top_categories()), mimetype='application/json')


@app.route('/get/sub_category_<cat_id>.json', methods=['GET', 'POST'])
def get_sub_categories_product(cat_id):
    """
    Get all sub-categories by category ID from the OC DB.
    :return: single json.
    """
    category_id = int(cat_id)
    mycategories = web.categories(mysqlcon)
    products = mycategories.get_sub_categories_to_top(category_id)
    return Response(json.dumps(products), mimetype='application/json')


@app.route('/get/products_by_cat_id_<cat_id>', methods=['GET', 'POST'])
def get_product_by_cat_id(cat_id):
    """
    Get all products by category ID from the OC DB.
    :return: single json.
    """
    category_id = int(cat_id)
    mycategories = web.categories(mysqlcon)
    products = mycategories.get_products_by_category(category_id)
    return Response(json.dumps(products, use_decimal=True), mimetype='application/json')


@app.route('/get/product_by_id_<product_id>', methods=['GET', 'POST'])
def get_product_cat_id(product_id):
    """
    Get product by product ID from the OC DB.
    :return: single json.
    """
    product_id = int(product_id)
    current_product = web.product(product_id, mysqlcon)
    current_product.product['date_added'] = ''
    current_product.product['date_available'] = ''
    current_product.product['date_modified'] = ''
    current_product.product['price'] = ''
    return Response(json.dumps(current_product.product, use_decimal=True), mimetype='application/json')


@app.route('/')
def hello_world():
    return 'To see a site map go to %s'%url_for('site_map')

@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and len(rule.defaults) >= len(rule.arguments):
            url = url_for(rule.endpoint)
            links.append((url, rule.endpoint))



if __name__ == '__main__':
    app.run(host='0.0.0.0')
