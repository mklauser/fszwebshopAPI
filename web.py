__author__ = 'michi'

import itertools
from flask import Flask, url_for
from jinja2.utils import Markup


class sidebar:
    def __init__(self, name=None):
        if name is None:
            self.name = "No name"
        else:
            self.name = name
        self.elements = dict()

    def set_name(self, name):
        self.name = name

    def add_entry(self, name, display_name, url, gray, enabled=False):
        entery_dict = dict()
        if name in self.elements.keys():
            raise 'Double name in sidebar dict'
        else:
            entery_dict['name'] = name
            entery_dict['url'] = url
            entery_dict['display_name'] = display_name
            entery_dict['enabled'] = enabled
            entery_dict['gray'] = gray
            self.elements[name] = entery_dict

            self.__dict__[name] = self.get_display_name(name)

    def get_display_name(self, name):
        return self.elements[name]['display_name']

    def get_url(self, name):
        return self.elements[name]['url']

    def get_enabled(self, name):
        return self.elements[name]['enable']

    def get_gray(self, name):
        return self.elements[name]['gray']

    def entries(self):
        return self.elements.keys()

    def iter_entries(self):
        for entry in self.elements:
            yield self.elements[entry]

    def set_enable_none(self):
        for entry in self.elements:
            print(self.elements[entry])
            self.elements[entry]['enabled'] = False

    def set_enable(self, name):
        for entry in self.elements:
            self.elements[entry]['enabled'] = False

        self.elements[name]['enabled'] = True


class product:
    def __init__(self, product_id, sql_conn):
        self.sql_conn = sql_conn
        self.product = sql_conn.get_product_by_id(product_id)[0]
        self.has_options = False

        try:
            self.product['manufacturer_name'] = sql_conn.get_manufacturer_by_id(self.product['manufacturer_id'])[0][
                'name']
        except:
            self.product['manufacturer_name'] = "None"
        self.product['categories'] = [a['name'] for a in self.sql_conn.get_categories_by_product_id(product_id)]
        self.product['display_description'] = Markup.unescape(Markup(self.product['display_description']))

        if self.sql_conn.has_product_options(product_id):
            self.has_options = True
            self.options = self.sql_conn.get_options_by_product(product_id)
            self.option_number = len(self.options)
            self.product['has_options'] = True
        else:
            self.options = dict()
            self.options['product_option_id'] = 0
            self.options['option_value_id'] = 0
            self.product['has_options'] = False
        self.product['options'] = self.options


class products:
    def __init__(self, sql_conn):
        self.sql_conn = sql_conn

    def get_products_by_category_id(self, category_id):
        return self.sql_conn.get_products_by_category(category_id)

    def get_products(self):
        return self.sql_conn.get_products()


class customers:
    def __init__(self, sql_conn):
        self.sql_conn = sql_conn
        self.customers = self.sql_conn.get_customers()
        self.customer_groups = self.sql_conn.get_customer_groups()
        self.current_customer_id = None
        self.__update_function_names()

    def get_customer_with_orderer(self):
        customers = self.sql_conn.get_customers()
        for cust in customers:
            cust['orderer'] = self.sql_conn.get_orderer(cust['customer_id'])
        return customers

    def set_group(self, group_id):
        self.customers = self.sql_conn.get_customers_by_groupe(group_id)
        self.__update_function_names()

    def set_no_filter(self):
        self.customers = self.sql_conn.get_customers()
        self.__update_function_names()

    def set_current_customer(self, customer_id):
        self.current_customer_id = customer_id
        self.current_customer = self.sql_conn.get_customers_by_customer_id(customer_id)

    def __update_function_names(self):
        print(self.customers)
        for customer in self.customers:
            customer['function_name'] = 'jsfunc_customer_' + str(customer['customer_id'])
        print(self.customers)


class cart:
    def __init__(self, sql_conn):
        self.customer_id = 0
        self.sql_conn = sql_conn
        self.products = dict()
        self.customer = 'None'
        self.customer_id = 0

    def get_key(self, product_id, product_option_id=None, option_value_id=None):
        print(product_id)
        print(product_option_id)
        print(option_value_id)
        if (product_option_id == None and option_value_id == None):
            product_option_id = 0
            option_value_id = 0
        key = str(product_id) + str(product_option_id) + str(option_value_id)
        print(key)
        return key


    def to_dict(self):
        self.cart_dict = dict()
        self.cart_dict['cart'] = self.products
        self.cart_dict['customer'] = self.customer
        self.cart_dict['customer_id'] = self.customer_id
        return self.cart_dict

    def from_dict(self, cart_dict):
        self.products = cart_dict['cart']
        self.customer = cart_dict['customer']
        self.customer_id = cart_dict['customer_id']

    def get_product(self, key):
        return self.products[key]

    def set_customer_id(self, customer_id):
        self.customer_id = customer_id
        self.customer = self.sql_conn.get_customers_by_customer_id(customer_id)


    def add_product(self, product_id, quantity, has_option=False, product_option_id=None, option_value_id=None, ):
        if has_option:
            print(product_id)
            print(product_option_id)
            print(option_value_id)
            in_cart_name = self.get_key(product_id, product_option_id=product_option_id,
                                        option_value_id=option_value_id)
        else:
            in_cart_name = self.get_key(product_id)

        if in_cart_name in self.products.keys():
            if quantity == 1:
                print(product_id)
                print(product_option_id)
                print(option_value_id)
                self.add_one_more(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
            else:
                self.add_many_more(quantity, product_id, product_option_id=product_option_id,
                                   option_value_id=option_value_id)
        else:

            product = dict()
            product['product_id'] = product_id
            product['in_cart_name'] = in_cart_name
            if quantity > 0:
                product['quantity'] = quantity
            else:
                product['quantity'] = 1
            if has_option:
                print(product_id, option_value_id)
                print(self.sql_conn.get_product_with_option(product_id, option_value_id))
                #get option details
                details = self.sql_conn.get_product_with_option(product_id, option_value_id)
                print(details)
                print(product_id, ' -- ', option_value_id)

                _tmp = details.copy()
                _tmp.update(product) # in case of a conflict the product dict has priority
                product = _tmp.copy()


                #get product details
                details = self.sql_conn.get_product_by_id(product_id)[0]
                _tmp = details.copy()
                _tmp.update(product) # in case of a conflict the product dict has priority
                product = _tmp.copy()

                product['product_option_id'] = product_option_id
                product['option_value_id'] = option_value_id
            else:
                details = self.sql_conn.get_product_by_id(product_id)[0]
                print(details)
                _tmp = details.copy()
                _tmp.update(product) # in case of a conflict the product dict has priority
                product = _tmp.copy()

                product['product_option_id'] = None
                product['option_value_id'] = None

            self.products[in_cart_name] = product

    def del_one_product(self, product_id, product_option_id=None, option_value_id=None):
        key = self.get_key(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
        if key in self.products.keys():
            del self.products[key]

    def add_one_more(self, product_id, product_option_id=None, option_value_id=None):
        key = self.get_key(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
        print(key)
        print(self.products.keys())
        self.products[key]['quantity'] += 1

    def add_many_more(self, quantity, product_id, product_option_id=None, option_value_id=None):
        key = self.get_key(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
        if quantity > 0:
            self.products[key]['quantity'] = quantity
        else:
            self.products[key]['quantity'] = 0

    def set_new_quantity(self, quantity, product_id, product_option_id=None, option_value_id=None):
        key = self.get_key(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
        if quantity > 0:
            self.products[key]['quantity'] = quantity

    def remove_one(self, product_id, product_option_id=None, option_value_id=None):
        key = self.get_key(product_id, product_option_id=product_option_id, option_value_id=option_value_id)
        if (self.products[key]['quantity'] - 1) > 0:
            self.products[key]['quantity'] -= 1
        else:
            self.del_one_product(key)

    def clear_cart(self):
        self.products = dict()


    def get_product_keys(self):
        for key in self.products.keys():
            yield key

    def get_products(self):
        for key in self.products.keys():
            yield self.products[key]


class categories:
    def __init__(self, sql_conn):
        self.sql_conn = sql_conn
        self.all_categories = self.sql_conn.get_categories()
        self.top_categories = self.sql_conn.get_top_categories()

    def get_top_categories(self):
        _top_categories = {}
        _top_categories['categories'] = self.top_categories
        return _top_categories

    def get_top_categories_with_subcat(self):
        _top_categories = {}
        _top_categories['categories'] = self.top_categories
        for cat in _top_categories['categories']:
            cat['sub_categories'] = self.get_sub_categories_to_top(
                cat['category_id'])
        return _top_categories



    def get_all_categories(self):
        return  self.all_categories

    def get_sub_categories_to_top(self, top_category_id):
        return self.sql_conn.get_sub_categories_for_top(top_category_id)

    def get_products_by_category(self, category_id):
        return self.sql_conn.get_products_by_category(category_id)

    def get_products_by_manufacturer(self, manufacturer_id):
        return self.sql_conn.get_products_by_manufacturer(manufacturer_id)

    def get_manufacturer(self):
        return self.sql_conn.get_manufacturers()

    def get_category_tree(self):
        cate_tree = dict()
        print(self.all_categories)
        for top in self.all_categories:
            cate_tree[top['category_id']] = top
            cate_tree[top['category_id']]['childs'] = self.get_sub_categories_to_top(top['category_id'])
        return cate_tree

