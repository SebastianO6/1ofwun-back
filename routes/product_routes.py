import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.product import Product
from models.user import User
from functools import wraps
import cloudinary.uploader

product_bp = Blueprint("product", __name__)

# -------------------------------
# Admin-only check
# -------------------------------
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


# -------------------------------
# GET all products
# -------------------------------
@product_bp.route("", methods=["GET"])
def list_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 6, type=int)

    products = Product.query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "items": [p.to_dict() for p in products.items],
        "total": products.total,
        "page": products.page,
        "per_page": products.per_page,
        "pages": products.pages
    })


# -------------------------------
# POST create product
# -------------------------------
@product_bp.route("", methods=["POST"])
@admin_required
def create_product():
    name = request.form.get("name")
    price = request.form.get("price")
    category = request.form.get("category")
    featured_raw = request.form.get("featured", "false")
    featured = str(featured_raw).lower() in ("true", "1", "yes", "on")

    if not (name and price):
        return jsonify({"msg": "name and price required"}), 400

    image_url = None
    image_pid = None
    image = request.files.get("image")
    if image:
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result["secure_url"]
        image_pid = upload_result["public_id"]

    prod = Product(
        name=name,
        price=float(price),
        category=category,
        featured=featured,
        image=image_url,
        image_public_id=image_pid
    )
    db.session.add(prod)
    db.session.commit()
    return jsonify(prod.to_dict()), 201


# -------------------------------
# PUT update product
# -------------------------------
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
        prod.featured = str(featured_raw).lower() in ("true", "1", "yes", "on")

    image = request.files.get("image")
    if image:
        # delete old image if exists
        if prod.image_public_id:
            try:
                cloudinary.uploader.destroy(prod.image_public_id)
            except Exception as e:
                print("⚠️ Failed to delete old image:", e)

        # upload new one
        upload_result = cloudinary.uploader.upload(image)
        prod.image = upload_result["secure_url"]
        prod.image_public_id = upload_result["public_id"]

    db.session.commit()
    return jsonify(prod.to_dict())


# -------------------------------
# DELETE product
# -------------------------------
@product_bp.route("/<int:pid>", methods=["DELETE"])
@admin_required
def delete_product(pid):
    prod = Product.query.get_or_404(pid)

    if prod.image_public_id:
        try:
            cloudinary.uploader.destroy(prod.image_public_id)
        except Exception as e:
            print("⚠️ Failed to delete image:", e)

    db.session.delete(prod)
    db.session.commit()
    return jsonify({"msg": "deleted"}), 200
