from datetime import datetime
from models import db

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default="pending")  # pending | completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.to_dict() if self.user else None,
            "total": self.total,
            "status": self.status,
            "items": [i.to_dict() for i in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
