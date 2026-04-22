# Simply Systems  API
REST + real-time API for the Simply Systems app — a tool for plural systems to manage alters, track fronting, and chat internally.

Built with **Python + Flask** (modular routes/models/extensions) and designed for scalability.

**Current status**: Online-only. All data stored on server (SQLite for dev, PostgreSQL for production).

## Updates
**I have stopped development for the most part on this project. If it gets enough attention, I will pick development back up and develop more features. Let me know if I shoudl continue development or not : )**


## Current Features

- **Authentication**  
  Register / login with JWT tokens  
  Get / update user profile (display name, system owner flag)

- **Members (alters) CRUD**  
  Create, read, update, delete members (name, pronouns, description, color)

- **Persistent fronting**  
  Set current fronter + start time  
  Auto-log fronting sessions with end time & duration

- **Fronting history**  
  Full list of fronting sessions (GET /api/front-history)

- **Internal group chat**  
  Real-time system-wide chat via Socket.IO  
  Messages saved in DB, broadcast to room `system_<user_id>`

- **Database**  
  SQLite (development) / PostgreSQL (production) via Flask-SQLAlchemy

- **Security**  
  JWT auth, bcrypt password hashing, basic input validation

## Tech Stack

- Python 3.10–3.12
- Flask 3.x
- Flask-SQLAlchemy + SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-SocketIO + python-socketio
- PostgreSQL (production) / SQLite (dev)
- Gunicorn (production server)
- python-dotenv (env vars)


### Prerequisites

- Python 3.10+
- PostgreSQL (optional; SQLite works fine)
- Git

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Vayrian/Simply-systems-api.git
   cd simply-plural-api

2. Create & activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Create .env file in root 
   ```bash
   SECRET_KEY=your-long-random-secret-key-here
   JWT_SECRET_KEY=another-long-random-secret-key-here
   DATABASE_URL=sqlite:///simply.db  # for local dev
   # For PostgreSQL (recommended for testing production):
   # DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/simply
   FLASK_DEBUG=True
5. Run the server:
   ```bash
   python app.py
   
   
API should be live at:
http://localhost:5000

### Test Endpoints (with curl or Postman)

- Health check: `curl http://localhost:5000/api/health`
- Register: `curl -X POST http://localhost:5000/api/register \`
`  -H "Content-Type: application/json" \`
 ` -d '{"email":"test@example.com","password":"password123"}'`
- Login (get JWT token): `curl -X POST http://localhost:5000/api/login \`
`  -H "Content-Type: application/json" \`
`  -d '{"email":"test@example.com","password":"password123"}'`
- Get profile (use token from login): `curl http://localhost:5000/api/user/profile \`
`  -H "Authorization: Bearer YOUR_JWT_TOKEN"`
- Socket.IO chat: connect via socket.io-client or Flutter client

### Deployment (Production)
Recommended: Render (free starter tier, auto-deploys from GitHub, built-in Postgres)
See Render docs: https://render.com/docs/deploy-flask


### Contributing

- Fork the repo
- Create feature branch (git checkout -b feature/add-polls)
- Commit changes
- Push & open Pull Request

All contributions must be licensed under the same license as the project.
### License
GNU Affero General Public License v3.0 (AGPL-3.0)
See LICENSE for full text.


Built with ♥ for plural systems.
