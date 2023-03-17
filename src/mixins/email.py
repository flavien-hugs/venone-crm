from datetime import date
from threading import Thread

from flask import current_app
from flask import render_template
from flask_mail import Message
from src import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_email_reminder(tenant, house):
    today = date.today()
    if (
        today >= house.vn_house_lease_start_date
        and today < house.vn_house_lease_end_date
    ):
        print(f"Email sent to {tenant.vn_addr_email}")
        send_email(
            tenant.vn_addr_email,
            f"Paiement de votre loyer du mois de {today}",
            "message/email",
            tenant=tenant,
            today=today,
        )
