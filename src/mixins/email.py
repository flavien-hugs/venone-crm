from threading import Thread

from flask import current_app
from flask import render_template
from flask_mail import Message
from src.exts import mail


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
    date = house.vn_house_lease_end_date
    send_email(
        tenant.vn_addr_email,
        f"Paiement de votre loyer du mois de {date}",
        "message/email",
        tenant=tenant,
        house=house,
    )
