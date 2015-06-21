__author__ = 'michi'
# This file handel's the connection to the SQL db
import MySQLdb
from functools import wraps

from flask import request


def cached(timeout=5 * 60, key='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv

        return decorated_function

    return decorator


class db_conn:
    """
    DB_CONN

    """
    __name__ = 'db_conn'


    def __init__(self, app):
        self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.config.setdefault('MYSQL_DATABASE_HOST', 'localhost')
        self.app.config.setdefault('MYSQL_DATABASE_PORT', 3306)
        self.app.config.setdefault('MYSQL_DATABASE_USER', None)
        self.app.config.setdefault('MYSQL_DATABASE_PASSWORD', None)
        self.app.config.setdefault('MYSQL_DATABASE_DB', None)
        self.app.config.setdefault('MYSQL_DATABASE_CHARSET', 'utf8')


    def connect(self):
        kwargs = {}
        if self.app.config['MYSQL_DATABASE_HOST']:
            kwargs['host'] = self.app.config['MYSQL_DATABASE_HOST']
        if self.app.config['MYSQL_DATABASE_PORT']:
            kwargs['port'] = self.app.config['MYSQL_DATABASE_PORT']
        if self.app.config['MYSQL_DATABASE_USER']:
            kwargs['user'] = self.app.config['MYSQL_DATABASE_USER']
        if self.app.config['MYSQL_DATABASE_PASSWORD']:
            kwargs['passwd'] = self.app.config['MYSQL_DATABASE_PASSWORD']
        if self.app.config['MYSQL_DATABASE_DB']:
            kwargs['db'] = self.app.config['MYSQL_DATABASE_DB']
        if self.app.config['MYSQL_DATABASE_CHARSET']:
            kwargs['charset'] = self.app.config['MYSQL_DATABASE_CHARSET']
        self.sql_conn = MySQLdb.connect(**kwargs)

    def query_db(self, query, args=()):
        cur = self.get_curser()
        cur.execute(query, args)
        description = cur.description
        rv = cur.fetchall()
        rv_dict = [dict(line) for line in [zip([column[0] for column in description], row) for row in rv]]
        return rv_dict

    def get_curser(self):
        if hasattr(self, 'sql_conn'):
            return self.sql_conn.cursor()
        else:
            self.connect()
            return self.sql_conn.cursor()

    def get_customers(self):
        select_cust_q = "SELECT customer_id, firstname, lastname, customer_group_id FROM `oc_customer`"
        custemers = self.query_db(select_cust_q)
        return custemers

    def get_orderer(self,customer_id):
        select_cust_q = "SELECT address_id, firstname, lastname, company, address_1, address_2, city, postcode FROM oc_address WHERE" \
                         " customer_id = %s"
        orderer = self.query_db(select_cust_q, args=(customer_id))
        return orderer

    @cached
    def get_customer_groups(self):
        select_cust_grou_q = "SELECT customer_group_id, name, description FROM oc_customer_group_description"
        customer_groups = self.query_db(select_cust_grou_q)
        return customer_groups

    def get_customers_by_groupe(self, customer_group_id):
        select_cust_q = "SELECT customer_id, firstname, lastname FROM oc_customer WHERE customer_group_id = %s "
        print(select_cust_q)
        custemers = self.query_db(select_cust_q, args=(customer_group_id))
        return custemers

    def get_customers_by_customer_id(self, customer_id):
        """
        returns dict
        ['customer_id']
        ['firstname']
        ['lastname']
        """
        select_cust_cust_q = 'SELECT customer_id, firstname, lastname FROM oc_customer WHERE customer_id = %s'
        custemer = self.query_db(select_cust_cust_q, args=(customer_id))[0]
        return custemer

    def get_manufacturers(self):
        select_mane_q = "SELECT manufacturer_id, name FROM oc_manufacturer"
        manufacturers = self.query_db(select_mane_q)
        return manufacturers

    def get_manufacturer_by_id(self, manufacturer_id):
        select_mane_name_q = 'SELECT name FROM oc_manufacturer WHERE manufacturer_id =%s'
        manufacturer = self.query_db(select_mane_name_q, args=(manufacturer_id))
        return manufacturer


    def get_products(self):
        select_prod_q = 'SELECT oc_product.product_id, oc_product.model, oc_product.ean, oc_product.location, oc_product.manufacturer_id, oc_product.price, oc_product_description.name ,oc_product_description.description FROM oc_product JOIN oc_product_description ON oc_product.product_id = oc_product_description.product_id ORDER BY oc_product.sort_order ASC'
        products = self.query_db(select_prod_q)
        return products


    def get_products_by_category(self, category_id):
        select_prod_cate_q = 'SELECT pr.product_id, pr.model, pr.ean, pr.location, pr.manufacturer_id, pr.price, oc_product_description.name ,oc_product_description.description FROM oc_product pr JOIN oc_product_to_category ON pr.product_id = oc_product_to_category.product_id JOIN oc_product_description ON pr.product_id = oc_product_description.product_id WHERE oc_product_to_category.category_id = %s ORDER BY pr.sort_order ASC'
        products = self.query_db(select_prod_cate_q, args=(category_id))
        return products


    def get_categories_by_product_id(self, product_id):
        """
        returns dict
        ['category_id']
        ['name']
        ['description']
        """
        select_cate_prod_q = 'SELECT oc_category_description.category_id, oc_category_description.name, oc_category_description.description FROM oc_category_description INNER JOIN oc_product_to_category ON oc_category_description.category_id = oc_product_to_category.category_id WHERE oc_product_to_category.product_id =%s'
        categories = self.query_db(select_cate_prod_q, args=(product_id))
        return categories


    def get_manufacturer_by_product_id(self, product_id):
        """
        returns dict
        ['manufacturer_id'] =manufacturer_id
        ['name'] = name
        """
        select_manu_prod_q = 'SELECT oc_manufacturer.manufacturer_id, oc_manufacturer.name FROM oc_manufacturer INNER JOIN oc_product ON oc_manufacturer.manufacturer_id = oc_product.manufacturer_id WHERE oc_product.product_id =%s'
        manufacturer = self.query_db(select_manu_prod_q, args=(product_id))
        return manufacturer


    def get_products_by_manufacturer(self, manufacturer_id):
        select_prod_q = 'SELECT oc_product.product_id, oc_product.model, oc_product.ean, oc_product.location, oc_product.manufacturer_id, oc_product.price ,oc_product_description.name as display_name,oc_product_description.description as display_description  FROM oc_product JOIN oc_product_description ON oc_product.product_id= oc_product_description.product_id WHERE oc_product.manufacturer_id = %s ORDER BY oc_product.sort_order ASC'
        products = self.query_db(select_prod_q, args=(manufacturer_id))
        return products


    def get_product_by_id(self, product_id):
        select_prod_q = 'SELECT *,oc_product_description.name as display_name,oc_product_description.description as display_description  FROM oc_product JOIN oc_product_description ON oc_product.product_id= oc_product_description.product_id WHERE oc_product.product_id = %s'
        product = self.query_db(select_prod_q, args=(product_id))
        return product


    def has_product_options(self, product_id):
        """
        Returns the number of options for a given product_id. If the product has no options it returns 0.
        """
        select_prod_opti_q = 'SELECT product_option_id, product_id, option_id FROM oc_product_option WHERE product_id = %s'
        options = self.query_db(select_prod_opti_q, args=(product_id))
        if len(options) == 0:
            return 0
        else:
            return len(options)


    def get_options_by_product(self, product_id):

        select_opti_prod_q = ("\n"
                              "        SELECT  oc_product.model, oc_product.location, oc_product_option_value.product_option_id as product_option_id , oc_product_option_value.product_id as product_id, oc_product_option_value.product_option_value_id as product_option_value_id,\n"
                              "        oc_option_description.name as option_description_name ,oc_product_option_value.quantity, oc_product_option_value.price, oc_option_value_description.name as option_value_description,  oc_option_value_description.option_value_id\n"
                              "        FROM oc_product_option_value\n"
                              "        JOIN oc_option_description ON oc_product_option_value.option_id = oc_option_description.option_id\n"
                              "        JOIN oc_option_value_description ON oc_product_option_value.option_value_id = oc_option_value_description.option_value_id\n"
                              "        JOIN oc_product ON oc_product_option_value.product_id = oc_product.product_id\n"
                              "        WHERE oc_product_option_value.product_id =%s \n"
                              "        "
        )
        # select_opti_prod_q='SELECT * FROM  oc_product_option_value JOIN oc_product_option ON  oc_product_option_value.option_id = oc_product_option.option_id WHERE oc_product_option.product_id = %s'
        options = self.query_db(select_opti_prod_q, args=(product_id))
        return options


    def get_product_with_option(self, product_id, option_value_id):
        select_prod_q = ("\n"
                         "        SELECT  oc_product.model, oc_product.location, oc_product_option_value.product_option_id as product_option_id , oc_product_option_value.product_id as product_id, oc_product_option_value.product_option_value_id as product_option_value_id,\n"
                         "        oc_option_description.name as option_description_name ,oc_product_option_value.quantity, oc_product_option_value.price, oc_option_value_description.name as option_value_description,  oc_option_value_description.option_value_id\n"
                         "        FROM oc_product_option_value\n"
                         "        JOIN oc_option_description ON oc_product_option_value.option_id = oc_option_description.option_id\n"
                         "        JOIN oc_option_value_description ON oc_product_option_value.option_value_id = oc_option_value_description.option_value_id\n"
                         "        JOIN oc_product ON oc_product_option_value.product_id = oc_product.product_id\n"
                         "        WHERE oc_product_option_value.product_id =%s AND  oc_option_value_description.option_value_id  =  %s\n"
                         "        "
        )
        product = self.query_db(select_prod_q, args=(product_id, option_value_id))[0]
        return product


    def get_top_categories(self):
        select_cate_q = """ SELECT oc_category.category_id, oc_category.image, oc_category.sort_order,  oc_category_description.name,oc_category_description.description
                            FROM oc_category
                            JOIN oc_category_description ON oc_category.category_id = oc_category_description.category_id
                            WHERE oc_category.status = 1 AND oc_category.top = 1 ORDER BY oc_category.sort_order ASC
                        """
        top_categories = self.query_db(select_cate_q)
        return top_categories


    def get_categories(self):
        select_cate_q = """ SELECT oc_category.category_id, oc_category.image, oc_category.sort_order,  oc_category_description.name,oc_category_description.description
                            FROM oc_category
                            JOIN oc_category_description ON oc_category.category_id = oc_category_description.category_id
                            WHERE oc_category.status = 1 ORDER BY oc_category.sort_order ASC
                        """
        categories = self.query_db(select_cate_q)
        return categories


    def get_sub_categories_for_top(self, top_category_id):

        select_cate_q = """ SELECT oc_category.category_id, oc_category.image, oc_category.sort_order,  oc_category_description.name,oc_category_description.description
                            FROM oc_category
                            JOIN oc_category_description ON oc_category.category_id = oc_category_description.category_id
                            WHERE oc_category.status = 1 AND oc_category.top = 0 AND oc_category.parent_id = %s ORDER BY oc_category.sort_order ASC
                        """
        sub_categories = self.query_db(select_cate_q, args=(top_category_id))
        return sub_categories


        #    def place_order