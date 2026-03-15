# init_db.py – one-time DB table creation for Render
from app import db, create_app

app = create_app()

with app.app_context():
    db.create_all()
    print("All tables created successfully!")