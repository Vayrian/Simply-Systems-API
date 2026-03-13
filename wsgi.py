# wsgi.py – entry point for production servers (Gunicorn, Render, etc.)
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()