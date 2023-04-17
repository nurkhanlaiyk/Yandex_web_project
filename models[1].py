import flask_login

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __str__(self):
        return f"User('{self.username}', '{self.email}')"


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(100), nullable=False)
    document_link = db.Column(db.String(200), nullable=False)
    doc_size = db.Column(db.Float, nullable=False)
    is_private = db.Column(db.Boolean, default=True, nullable=True)

    def __init__(self, user_id, name, document_link, doc_size, is_private: bool = False):
        self.user_id = user_id
        self.name = name
        self.document_link = document_link
        self.doc_size = doc_size
        self.is_private = is_private

    def __str__(self):
        return self.name


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"), nullable=False)
    document = db.relationship("Document", backref=db.backref("favorites", lazy=True))
    user = db.relationship("User", backref=db.backref("favorites", lazy=True))

    def __str__(self):
        return f"Favorite document_id={self.document_id}"
