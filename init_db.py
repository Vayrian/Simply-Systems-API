# init_db.py – One-time script to create all tables in the database
# Run this manually on Render console or as part of first deploy

from app import create_app, db  # Import the factory and db instance

app = create_app()  # This creates the Flask app and initializes db, extensions, etc.

with app.app_context():
    db.create_all()
    print("All database tables created successfully!")