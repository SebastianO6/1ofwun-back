from datetime import datetime
from models import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), index=True)
    image = db.Column(db.String(512))
    image_public_id = db.Column(db.String(255)) 
    featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    thumbnail = db.Column(db.String(512))


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "image": self.image,               
            "thumbnail": self.thumbnail,       
            "image_public_id": self.image_public_id,
            "featured": self.featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

