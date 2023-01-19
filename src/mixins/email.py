from threading import Thread

from flask import current_app
from flask import render_template
from flask_mail import Message

from .. import mail


def send_async_email(app, to, subject, template, **kwargs):
    with app.app_context():
        msg = Message(subject, recipients=[to])
        msg.body = render_template(template + ".txt", **kwargs)
        msg.html = render_template(template + ".html", **kwargs)
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    thr = Thread(
        target=send_async_email, args=(app, to, subject, template), kwargs=kwargs
    )
    thr.start()
    return thr
