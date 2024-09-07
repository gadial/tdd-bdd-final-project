# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_product_read(self):
        """It should read a product"""
        product = ProductFactory()
        app.logger.info("Product generated: ", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product_from_db = Product.find(product.id)
        self.assertEqual(product.name, product_from_db.name)
        self.assertEqual(product.description, product_from_db.description)
        self.assertEqual(product.price, product_from_db.price)
        self.assertEqual(product.available, product_from_db.available)
        self.assertEqual(product.category, product_from_db.category)

    def test_product_update(self):
        """It should update a product"""
        product = ProductFactory()
        app.logger.info("Product generated: ", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info("Product created in db: ", product)
        new_description_string = "New description"
        product.description = new_description_string
        original_product_id = product.id
        product.update()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product_from_db = products[0]
        self.assertEqual(product_from_db.description, new_description_string)
        self.assertEqual(product_from_db.id, original_product_id)

    def test_product_delete(self):
        """It should delete a product"""
        product = ProductFactory()
        app.logger.info("Product generated: ", product)
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        num_products = 5
        for _ in range(num_products):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), num_products)

    def test_find_product_by_name(self):
        """It find a product by name"""
        num_products = 5
        products_list = [ProductFactory() for _ in range(num_products)]
        for product in products_list:
            product.create()
        name_to_find = products_list[0].name
        num_occurances_in_list = len([product for product in products_list if product.name == name_to_find])
        found_products = Product.find_by_name(name_to_find)
        self.assertEqual(found_products.count(), num_occurances_in_list)
        for product in found_products:
            self.assertEqual(product.name, name_to_find)

    def test_find_product_by_availability(self):
        """It find a product by availability"""
        num_products = 10
        products_list = [ProductFactory() for _ in range(num_products)]
        for product in products_list:
            product.create()
        available = products_list[0].available
        num_occurances_in_list = len([product for product in products_list if product.available == available])
        found_products = Product.find_by_availability(available)
        self.assertEqual(found_products.count(), num_occurances_in_list)
        for product in found_products:
            self.assertEqual(product.available, available)

    def test_find_product_by_category(self):
        """It find a product by category"""
        num_products = 10
        products_list = [ProductFactory() for _ in range(num_products)]
        for product in products_list:
            product.create()
        category = products_list[0].category
        num_occurances_in_list = len([product for product in products_list if product.category == category])
        found_products = Product.find_by_category(category)
        self.assertEqual(found_products.count(), num_occurances_in_list)
        for product in found_products:
            self.assertEqual(product.category, category)

    def test_find_product_by_price(self):
        """It find a product by price"""
        num_products = 10
        products_list = [ProductFactory() for _ in range(num_products)]
        for product in products_list:
            product.create()
        price = products_list[0].price
        num_occurances_in_list = len([product for product in products_list if product.price == price])
        found_products = Product.find_by_price(price)
        self.assertEqual(found_products.count(), num_occurances_in_list)
        for product in found_products:
            self.assertEqual(product.price, price)

        found_products = Product.find_by_price(str(price))
        self.assertEqual(found_products.count(), num_occurances_in_list)
        for product in found_products:
            self.assertEqual(product.price, price)
