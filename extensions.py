from flask_sqlalchemy import SQLAlchemy

# Create the extension independently; bind it to the Flask app in create_app().
db = SQLAlchemy()
