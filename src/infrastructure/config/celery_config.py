from celery import Celery, Task


def celery_init_app(app):
    """Celery setup for Flask application context."""
    celery_app = Celery(
        app.name,
        broker_url=app.config.get("CELERY_BROKER_URL"),
        result_backend=app.config.get("CELERY_BROKER_URL"),
    )
    celery_app.conf.update(app.config)

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            if not app:
                return self.run(*args, **kwargs)
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app
