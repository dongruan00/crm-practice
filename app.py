from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from extensions import db
from routes import customer_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(customer_bp)

    # Import model definitions before create_all() registers mapped tables.
    from models import Customer  # noqa: F401

    with app.app_context():
        db.create_all()

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        db.session.rollback()
        app.logger.exception("Database operation failed: %s", error)
        return jsonify({
            "code": 500,
            "message": "数据库操作失败",
            "data": None,
        }), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Flask's built-in server is for local development only.
    app.run(debug=app.config.get("DEBUG", False))
