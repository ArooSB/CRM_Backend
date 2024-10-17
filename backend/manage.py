from flask_migrate import Migrate
from backend import create_app
from backend.models import *
from sqlalchemy import inspect
from flask_migrate import upgrade

app = create_app()
migrate = Migrate(app, db)

@app.cli.command('create_db')
def create_db():
    """Create the database and all necessary tables."""
    with app.app_context():
        db.create_all()
        print("Database and tables created successfully.")

@app.cli.command('drop_db')
def drop_db():
    """Drop all tables in the database."""
    with app.app_context():
        db.drop_all()
        print("All tables dropped successfully.")

@app.cli.command('seed_db')
def seed_db():
    """Seed the database with an initial admin user.

    This command checks if the 'workers' table exists and seeds the
    database with an initial admin user if none exists. If the admin
    user already exists, it prints a message indicating so.
    """
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            if not inspector.has_table('workers'):
                print("Error: 'workers' table does not exist. Please run 'create_db' first.")
                return

            admin = Worker.query.filter_by(email='admin@example.com').first()
            if not admin:
                admin = Worker(
                    username='admin',  # Set a username for the admin
                    first_name='Admin',
                    last_name='User',
                    email='admin@example.com',
                    position='admin'
                )
                admin.set_password('admin_password')
                db.session.add(admin)
                db.session.commit()
                print("Admin user seeded into the database.")
            else:
                print("Admin user already exists.")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")

@app.cli.command('reset_db')
def reset_db():
    """Reset the database by dropping, creating, and seeding it."""
    drop_db()
    create_db()
    seed_db()
    print("Database has been reset and seeded with initial data.")

@app.cli.command('list_users')
def list_users():
    """List all users in the database."""
    with app.app_context():
        try:
            users = Worker.query.all()
            if users:
                print("List of users:")
                for user in users:
                    print(f"ID: {user.id}, Name: {user.first_name} {user.last_name}, Email: {user.email}, Position: {user.position}")
            else:
                print("No users found.")
        except Exception as e:
            print(f"Error listing users: {str(e)}")

@app.cli.command('db_upgrade')
def upgrade_db():
    """Apply migrations to upgrade the database."""
    with app.app_context():
        try:
            upgrade()  # Run migrations
            print("Database upgraded successfully!")
        except Exception as e:
            print(f"Error upgrading database: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, port=5003)
