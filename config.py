
#  -----------------------------------------------------------------------------
#  Simply Systems
#  A mobile app (iOS & Android) for plural systems to manage system members,
#  track fronting history, communicate internally via real-time chat, etc.
# -----------------------------------------------------------------------------
#  Copyright (C) 2026 Vayrian

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see https://www.gnu.org/licenses/.


import os
from datetime import timedelta

# Load environment variables from .env file (for local dev)
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Secret keys (use strong random values in production!)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me-immediately')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Database – use PostgreSQL on Railway, fallback to SQLite for local
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///simply.db'  # fallback for local development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'