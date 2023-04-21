import sys
import unittest

from flask import current_app
from src import create_venone_app
from src import db

sys.path.append("..")


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.app = create_venone_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])


if __name__ == "__main__":
    unittest.main()
