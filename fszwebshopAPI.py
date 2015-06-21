import simplejson as json

from flask import Flask, Response, url_for, render_template
from flask.ext.cors import CORS

import web
import sql


app = Flask(__name__)
app.config.from_object('config')
app.config.items()

app.test_request_context()

cors = CORS(app)

mysqlcon = sql.db_conn(app)
data = mysqlcon.get_customers()
mycucustomers = web.customers(mysqlcon)


@app.route('/get/customer', methods=['GET'])
def get_customers():
    """
    Get all available customers from the OC DB.
    :return: single json.
    """
    return Response(json.dumps(mycucustomers.get_customer_with_orderer()),  mimetype='application/json')



@app.route('/get/categories', methods=['GET'])
def get_categories():
    """
    Get all available categories from the OC DB.
    :return: single json.
    """
    mycategories = web.categories(mysqlcon)

    return Response(json.dumps(mycategories.get_top_categories()), mimetype='application/json')


@app.route('/get/categories_with_subcat', methods=['GET'])
def get_categories_with_subcat():
    """
    Get all available categories from the OC DB.
    :return: single json.
    """
    mycategories = web.categories(mysqlcon)

    return Response(json.dumps(mycategories.get_top_categories_with_subcat()), mimetype='application/json')


@app.route('/get/sub_category_<cat_id>', methods=['GET', 'POST'])
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
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    return render_template("all_links.html", links=output)



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
