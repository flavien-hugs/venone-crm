from flask import render_template, url_for


def register_error_handlers(app):
    @app.errorhandler(400)
    def key_error(e):
        image_path = url_for("static", filename="img/error/404.svg")
        return (
            render_template(
                "pages/error.html",
                page_title=e.name,
                image_path=image_path,
                error=e,
            ),
            400,
        )

    @app.errorhandler(403)
    def forbidden(e):
        image_path = url_for("static", filename="img/error/403.svg")
        return (
            render_template(
                "pages/error.html",
                page_title=f"erreur {e}",
                image_path=image_path,
                error=e,
            ),
            403,
        )

    @app.errorhandler(404)
    def page_not_found(e):
        image_path = url_for("static", filename="img/error/404.svg")
        return (
            render_template(
                "pages/error.html",
                page_title=e.name,
                image_path=image_path,
                error=e,
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_server_error(e):
        image_path = url_for("static", filename="img/error/500.svg")
        return (
            render_template(
                "pages/error.html",
                page_title=e.name,
                image_path=image_path,
                error=e,
            ),
            500,
        )
