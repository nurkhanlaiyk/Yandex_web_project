import os

from flask import Flask, request, redirect, render_template, url_for, jsonify
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.utils import secure_filename

from models import User, Document, Favorite
from utils import allowed_file, generate_unique_filename
from models import db

app = Flask(__name__)
app.secret_key = "secret"
bcrypt = Bcrypt(app)

# Configure the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db.init_app(app)
app.config["UPLOAD_FOLDER"] = "static/"

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("home/index.html")


# Route for the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode(
            "utf-8"
        )
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/")

    return render_template("auth/register.html")


# Route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")
        else:
            return render_template(
                "auth/login.html", error="Invalid username or password"
            )
    return render_template("auth/login.html")


# Route for the logout page
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# upload file
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(
                f"{generate_unique_filename()}.{file.filename.rsplit('.', 1)[1]}"
            )
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            private = True
            if "all_files" in request.referrer:
                private = False
            document = Document(
                user_id=current_user.id,
                name=file.filename,
                document_link=os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename,
                ),
                doc_size=os.path.getsize(
                    os.path.join(app.config["UPLOAD_FOLDER"], filename)
                ),
                is_private=private,
            )
            db.session.add(document)
            db.session.commit()
            if "all_files" in request.referrer:
                return redirect(url_for("all_files"))
            return redirect(url_for("files"))
    return redirect(url_for("files"))


# list files
@app.route("/files")
def files():
    if not current_user.is_authenticated:
        # Redirect to login page if user is not authenticated
        return redirect(url_for("login"))

    user_id = current_user.get_id()
    # Get all files.html associated with the current user
    documents = Document.query.filter_by(user_id=user_id).all()
    for document in documents:
        document.link = str(document.document_link).split("/")[1]
        document.doc_size = int(document.doc_size / 1024)
    return render_template("files/files.html", documents=documents)


@app.route("/all_files")
def all_files():
    if not current_user.is_authenticated:
        # Redirect to login page if user is not authenticated
        return redirect(url_for("login"))

    # Get all files.html associated with the current user
    documents = Document.query.filter_by(is_private=False).all()
    for document in documents:
        document.link = str(document.document_link).split("/")[1]
        document.doc_size = int(document.doc_size / 1024)
        document.user = User.query.filter_by(id=document.user_id).first()

    return render_template("files/all_files.html", documents=documents)


@app.route("/like/<int:pk>", methods=["GET", "POST"])
@login_required
def like(pk):
    favorite = Favorite.query.filter_by(user_id=current_user.id, document_id=pk).first()
    if not favorite:
        favorite = Favorite(user_id=current_user.id, document_id=pk)
        db.session.add(favorite)
        db.session.commit()

    return redirect(url_for("all_files"))


@app.route("/delete/<int:pk>", methods=["GET", "POST"])
@login_required
def delete(pk):
    favorite = Favorite.query.filter_by(user_id=current_user.id, document_id=pk).first()
    print(favorite)
    if favorite:
        db.session.delete(favorite)
        db.session.commit()

    return redirect(url_for("favorites"))


@app.route("/favorites", methods=["GET"])
def favorites():
    user = User.query.get(current_user.id)
    documents = [favorite.document for favorite in user.favorites]
    for document in documents:
        document.link = str(document.document_link).split("/")[1]
        document.doc_size = int(document.doc_size / 1024)

    return render_template("files/favorites.html", documents=documents)


# Here REST API


@app.route("/api/register", methods=["POST"])
def api_register():
    username = request.form["username"]
    email = request.form["email"]
    password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    user = User.query.filter_by(username=request.form["username"]).first()
    if user and bcrypt.check_password_hash(user.password, request.form["password"]):
        login_user(user)
        return jsonify({"message": "User logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 400


@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()

    return jsonify({"message": "User logged out successfully"}), 200


@app.route("/api/upload", methods=["POST"])
@login_required
def api_upload_file():
    file = request.files["file"]
    if file and allowed_file(file.filename):
        filename = secure_filename(
            f"{generate_unique_filename()}.{file.filename.rsplit('.', 1)[1]}"
        )
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        document = Document(
            user_id=current_user.id,
            name=file.filename,
            document_link=os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename,
            ),
            doc_size=os.path.getsize(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            ),
        )
        db.session.add(document)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully"}), 201

    return jsonify({"message": "File upload failed"}), 400


@app.route("/api/files", methods=["GET"])
def api_files():
    if not current_user.is_authenticated:
        return {"error": "Unauthorized"}, 401

    user_id = current_user.get_id()
    # Get all files associated with the current user
    documents = Document.query.filter_by(user_id=user_id).all()
    # Convert the result to a list of dictionaries
    documents_data = [
        {
            "name": document.name,
            "document_link": str(request.host_url) + document.document_link,
            "doc_size": int(document.doc_size / 1024),
        }
        for document in documents
    ]
    # Return the data as JSON
    return jsonify(documents_data)


# all files


@app.route("/api/all_files", methods=["GET"])
def api_all_files():
    documents = Document.query.all()
    document_list = [document.to_dict() for document in documents]

    return jsonify(document_list)


# like
@app.route("/api/like", methods=["POST"])
@login_required
def api_like(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    # Create a Favorite object to represent the like
    favorite = Favorite(user_id=current_user.id, document_id=document.id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Document liked successfully"})


@app.route("/api/delete", methods=["POST"])
@login_required
def api_delete(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"error": "Document not found"}), 404

    # Create a Favorite object to represent the like
    favorite = Favorite(user_id=current_user.id, document_id=document.id)
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Document deleted successfully"})


@app.route("/api/favorites", methods=["GET"])
def api_favorites():
    user = User.query.get(current_user.id)
    documents = [favorite.document for favorite in user.favorites]
    for document in documents:
        document.link = str(document.document_link).split("/")[1]
        document.doc_size = int(document.doc_size / 1024)
    document_list = [document.to_dict() for document in documents]

    return jsonify(document_list)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
