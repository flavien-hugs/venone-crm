from flask import url_for

from src.exts import db
from tests.base_case import BaseCase


class TestAuthApp(BaseCase):
    def test_login_page_loads(self):
        response = self.client.get("/auth/login/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Se connecter", response.data)

    def test_login_authenticated_user(self):
        with self.client:
            self.client.post(
                url_for("auth_bp.login"),
                data=dict(
                    email_or_phone=self.user.vn_addr_email,
                    password="password",
                    remember_me=False,
                ),
            )
            response = self.client.get(url_for("owner_bp.dashboard"))
            self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        with self.client:
            response = self.client.post(
                url_for("auth_bp.login"),
                data=dict(
                    email_or_phone=self.user.vn_addr_email,
                    password="wrong_password",
                    remember_me=False,
                ),
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)

    def test_login_inactive_user(self):
        with self.client:
            self.user.vn_activated = False
            db.session.commit()
            response = self.client.post(
                url_for("auth_bp.login"),
                data=dict(
                    email_or_phone=self.user.vn_addr_email,
                    password="password",
                    remember_me=False,
                ),
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)

    def test_logout_authenticated_user(self):
        with self.client:
            self.client.post(
                url_for("auth_bp.login"),
                data=dict(
                    email_or_phone=self.user.vn_addr_email,
                    password="password",
                    remember_me=False,
                ),
            )

            response = self.client.get(url_for("auth_bp.logout"), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
