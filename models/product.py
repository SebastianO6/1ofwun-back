from datetime import datetime
from flask import url_for
from models import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), index=True)
    image_filename = db.Column(db.String(256))
    featured = db.Column(db.Boolean, default=False, nullable=False)  # ✅ new field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def image_url(self):
        if not self.image_filename:
            return None
        return url_for("static", filename=f"uploads/{self.image_filename}", _external=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "image_url": self.image_url(),
            "featured": self.featured,  # ✅ include featured in response
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
