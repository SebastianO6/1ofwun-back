import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.product import Product
from models.user import User
from functools import wraps

product_bp = Blueprint("product", __name__)

# admin-only check
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user or not user.is_admin:
            return jsonify({"msg": "admins only"}), 403
        return fn(*args, **kwargs)
    return wrapper


# GET all products
@product_bp.route("", methods=["GET"])
def list_products():
    prods = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_dict() for p in prods])


# POST create product (accepts multipart form-data with optional image)
# POST create product
@product_bp.route("", methods=["POST"])
@admin_required
def create_product():
    name = request.form.get("name")
    price = request.form.get("price")
    category = request.form.get("category")
    featured_raw = request.form.get("featured", "false")
    featured = str(featured_raw).lower() in ("true", "1", "yes", "on")  # ✅ parse

    if not (name and price):
        return jsonify({"msg": "name and price required"}), 400

    filename = None
    image = request.files.get("image")
    if image:
        raw = secure_filename(image.filename)
        filename = f"{uuid.uuid4().hex}_{raw}"
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(path)

    prod = Product(
        name=name,
        price=float(price),
        category=category,
        featured=featured,  # ✅ save
        image_filename=filename,
    )
    db.session.add(prod)
    db.session.commit()
    return jsonify(prod.to_dict()), 201


# PUT update product
@product_bp.route("/<int:pid>", methods=["PUT"])
@admin_required
def update_product(pid):
    prod = Product.query.get_or_404(pid)
    data = request.form if request.form else (request.json or {})

    if "name" in data: prod.name = data["name"]
    if "price" in data: prod.price = float(data["price"])
    if "category" in data: prod.category = data["category"]

    if "featured" in data:
        featured_raw = data["featured"]
        prod.featured = str(featured_raw).lower() in ("true", "1", "yes", "on")  # ✅ update

    image = request.files.get("image")
    if image:
        raw = secure_filename(image.filename)
        filename = f"{uuid.uuid4().hex}_{raw}"
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(path)
        prod.image_filename = filename

    db.session.commit()
    return jsonify(prod.to_dict())



# DELETE product
@product_bp.route("/<int:pid>", methods=["DELETE"])
@admin_required
def delete_product(pid):
    prod = Product.query.get_or_404(pid)
    db.session.delete(prod)
    db.session.commit()
    return jsonify({"msg": "deleted"}), 200
