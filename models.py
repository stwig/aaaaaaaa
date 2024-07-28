from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON  # Use JSON type for PostgreSQL

db = SQLAlchemy()

class PDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)
    pdf_metadata = db.Column(db.JSON, nullable=False)
    description = db.Column(db.String(255))
    question = db.Column(db.String(255))
    case_field = db.Column(db.String(255))
    answer = db.Column(db.String(255))

class User(db.Model):
    username = db.Column(db.String(255), primary_key=True)
    pdf_ids = db.Column(db.JSON, default=[])  # Store PDF IDs as a list in JSON field

    def __init__(self, username):
        self.username = username
        self.pdf_ids = []
