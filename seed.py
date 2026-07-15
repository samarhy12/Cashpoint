"""
Seed the database with the default administrator account only.

This wipes the existing database and recreates the schema, then adds a single
admin user for initial login.

Usage:
    python seed.py
"""
from app import create_app
from extensions import db
from models import Staff


def main():
    app = create_app()
    with app.app_context():
        print(">> Resetting database and creating admin only...")
        db.drop_all()
        db.create_all()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("INITIAL_ADMIN_PASSWORD")
        if not password:
            raise RuntimeError("ADMIN_PASSWORD must be configured in the environment or .env file")

        admin = Staff(full_name="System Administrator", username=username, role="admin")
        admin.set_password(password)
        admin.must_change_password = True
        db.session.add(admin)
        db.session.commit()

        print(f">> Admin created — username: {username} / password: {password}")


if __name__ == "__main__":
    main()
