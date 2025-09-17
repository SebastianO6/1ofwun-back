import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from models import db, bcrypt
from models.user import User  
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.order_routes import order_bp
from routes.contact import contact_bp


def seed_admin(app):
    """Ensure an admin user exists."""
    with app.app_context():
        admin_email = os.getenv("ADMIN_EMAIL", "1ofwun25@gmail.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "pass12word@2025$")

        if User.query.filter_by(email=admin_email).first():
            print(f"ℹ️ Admin {admin_email} already exists")
            return

        hashed_pw = bcrypt.generate_password_hash(admin_password).decode("utf-8")
        admin = User(
            username="admin",
            email=admin_email,
            password_hash=hashed_pw,
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created: {admin_email}")


def create_app():
    """Flask application factory."""
    load_dotenv()
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or "sqlite:///dev.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this-in-prod")

    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": frontend_origin}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    app.url_map.strict_slashes = False

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")

    @app.route("/")
    def index():
        return jsonify({"message": "1OfWun API running"})

    seed_admin(app)

    return app


app = create_app()
