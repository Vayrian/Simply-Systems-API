
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


from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config
from extensions import db, jwt, socketio, migrate 

# Import blueprints (REST routes)
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.members import members_bp
from routes.fronting import fronting_bp
from routes.front_history import front_history_bp
from routes.messages import messages_bp

# Import socket handlers
from sockets.chat import init_socket_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize shared extensions
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    migrate.init_app(app, db)  # ← Enables flask db commands

    # Improved CORS: allow all origins + credentials + Socket.IO specific headers
    CORS(app, resources={
        r"/*": {
            "origins": "*",  
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "supports_credentials": True
        }
    })

    # Register REST API blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(members_bp, url_prefix='/api')
    app.register_blueprint(fronting_bp, url_prefix='/api')
    app.register_blueprint(front_history_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')

    # Register Socket.IO handlers
    init_socket_handlers(socketio)

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)