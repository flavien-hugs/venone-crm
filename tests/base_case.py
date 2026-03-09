import sys
import unittest

from flask import current_app

from helpers.plugins import db, login_manager
from main import create_app
from src.auth.models import User

sys.path.append("..")


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        login_manager.init_app(self.app)

        self.user = User(
            vn_gender="Mr",
            vn_fullname="Flavien HUGS",
            vn_addr_email="test@example.com",
            vn_phonenumber_one="1234567890",
            vn_cni_number="CI1234567890",
            vn_country="CI",
        )
        self.user.set_password("password")
        self.user.vn_activated = True
        self.user.vn_house_owner = True

        db.session.add(self.user)
        db.session.commit()

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
