from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.user import User

order_bp = Blueprint("order", __name__)

@order_bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"msg": "items required"}), 400

    total = 0.0
    order = Order(user_id=user_id, total=0.0, status="pending")
    db.session.add(order)
    db.session.flush()  # get order.id
    for it in items:
        pid = it.get("product_id")
        qty = int(it.get("quantity", 1))
        product = Product.query.get(pid)
        if not product:
            db.session.rollback()
            return jsonify({"msg": f"product {pid} not found"}), 400
        line_total = product.price * qty
        total += line_total
        oi = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, unit_price=product.price)
        db.session.add(oi)

    order.total = total
    db.session.commit()
    return jsonify(order.to_dict()), 201

@order_bp.route("", methods=["GET"])
@jwt_required()
def list_orders():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if user and user.is_admin:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=uid).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@order_bp.route("/<int:oid>", methods=["PATCH"])
@jwt_required()
def update_order(oid):
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or not user.is_admin:
        return jsonify({"msg": "admins only"}), 403
    order = Order.query.get_or_404(oid)
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ("pending", "completed"):
        return jsonify({"msg": "invalid status"}), 400
    order.status = new_status
    db.session.commit()
    return jsonify(order.to_dict())
