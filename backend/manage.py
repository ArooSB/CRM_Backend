from flask_migrate import Migrate, upgrade
from backend import create_app
from backend.models import Worker, db
from sqlalchemy import inspect
import click

app = create_app()
migrate = Migrate(app, db)

def with_app_context(func):
    """Decorator to simplify app context setup in CLI commands."""
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper

@app.cli.command("create_db")
@with_app_context
def create_db():
    """Create the database and all necessary tables."""
    try:
        db.create_all()
        print("✅ Database and tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating database and tables: {e}")

@app.cli.command("drop_db")
@with_app_context
def drop_db():
    """Drop all tables in the database."""
    try:
        db.drop_all()
        print("✅ All tables dropped successfully.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

@app.cli.command("seed_db")
@with_app_context
def seed_db():
    """Seed the database with an initial admin user if none exists."""
    try:
        if not inspect(db.engine).has_table("workers"):
            print("❌ Error: 'workers' table does not exist. Please run 'create_db' first.")
            return

        admin = Worker.query.filter_by(email="admin@example.com").first()
        if not admin:
            admin = Worker(
                username="admin",
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                position="admin"
            )
            admin.set_password("admin_password")  # Ensure set_password is secure
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user seeded into the database.")
        else:
            print("ℹ️  Admin user already exists.")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")

@app.cli.command("reset_db")
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset_db():
    """Reset the database by dropping, creating, and seeding it."""
    try:
        drop_db()
        create_db()
        seed_db()
        print("✅ Database has been reset and seeded with initial data.")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

@app.cli.command("list_users")
@with_app_context
def list_users():
    """List all users in the database."""
    try:
        users = Worker.query.all()
        if users:
            print("👥 List of users:")
            for user in users:
                print(f"ID: {user.id}, Name: {user.first_name} {user.last_name}, Email: {user.email}, Position: {user.position}")
        else:
            print("ℹ️  No users found.")
    except Exception as e:
        print(f"❌ Error listing users: {e}")

@app.cli.command("db_upgrade")
@with_app_context
def upgrade_db():
    """Apply migrations to upgrade the database."""
    try:
        upgrade()
        print("✅ Database upgraded successfully!")
    except Exception as e:
        print(f"❌ Error upgrading database: {e}")

if __name__ == "__main__":
    app.run()
    #app.run(debug=True, port=5003)