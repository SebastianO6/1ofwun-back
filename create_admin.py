import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from models import db
from models.user import User

app = create_app()

def main():
    with app.app_context():
        email = os.getenv("ADMIN_EMAIL") or input("Admin email: ")
        password = os.getenv("ADMIN_PASSWORD") or input("Admin password: ")

        existing_admin = User.query.filter(
            (User.email == email) | (User.username == "admin")
        ).first()

        if existing_admin:
            print("Admin already exists:", existing_admin.email)
            return

        admin = User(username="admin", email=email, is_admin=True)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin user created: {email}")

if __name__ == "__main__":
    main()
