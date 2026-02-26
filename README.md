# Cybersecurity Club Website

A modern, secure website for the APSIT Cybersecurity Club featuring event management, registration system, and resource library.

## 🚀 Features

- **Modern Frontend**: Responsive design with Three.js animations and dark mode
- **Secure Backend**: FastAPI with PostgreSQL, JWT authentication, and comprehensive security measures
- **Event Management**: Create, manage, and track events
- **Registration System**: Public event registration with duplicate prevention
- **Resource Library**: PDF resource upload and download system
- **Admin Dashboard**: Full CRUD operations for events and resources

## 📁 Project Structure

```
.
├── backend/          # FastAPI backend application
│   ├── app/         # Application code
│   ├── migrations/  # Database migrations
│   ├── scripts/     # Utility scripts
│   └── uploads/     # PDF storage
├── images/          # Frontend images
├── js/              # Frontend JavaScript
└── index.html       # Main frontend file
```

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Three.js for 3D animations
- GSAP for animations
- Font Awesome icons

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Authentication**: JWT + Argon2
- **Security**: Rate limiting, input sanitization, CORS protection

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker (optional, for containerized deployment)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/cybersec_club
   JWT_SECRET_KEY=your-secret-key-minimum-32-characters
   FRONTEND_URL=http://localhost:5500
   ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Seed database:**
   ```bash
   python scripts/seed_db.py
   ```

7. **Start backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Serve the frontend:**
   ```bash
   # Using Python
   python -m http.server 5500
   
   # Or using Node.js
   npx http-server -p 5500
   ```

2. **Open in browser:**
   ```
   http://localhost:5500
   ```

### Docker Setup (Alternative)

```bash
cd backend
docker-compose up -d
```

## 📚 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Default Admin Credentials

After seeding the database:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change the admin password immediately after first login!

## 📝 API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `GET /api/auth/me` - Get current user (protected)

### Events
- `GET /api/events` - List all events (public)
- `POST /api/events` - Create event (admin)
- `PUT /api/events/{id}` - Update event (admin)
- `DELETE /api/events/{id}` - Delete event (admin)

### Registrations
- `POST /api/registrations` - Register for event (public)
- `GET /api/registrations` - List registrations (admin)
- `GET /api/registrations/export/csv` - Export CSV (admin)

### Resources
- `GET /api/resources` - List resources (public)
- `POST /api/resources` - Upload PDF (admin)
- `GET /api/resources/{id}/download` - Download PDF (public)
- `DELETE /api/resources/{id}` - Delete resource (admin)

## 🔒 Security Features

- Argon2 password hashing
- JWT token authentication (1-hour expiration)
- Rate limiting (5/15min for login)
- Input sanitization (XSS prevention)
- PDF file validation (magic bytes verification)
- CORS protection
- Security headers (HSTS, CSP, X-Frame-Options)

## 📄 License

[Your License Here]

## 👥 Contributors

- [Your Name/Team]

## 📞 Contact

For questions or support, please contact: cyberclub@apsit.edu.in
