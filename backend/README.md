# Cybersecurity Club Backend API

Secure FastAPI backend for the Cybersecurity Club website with event management, registration system, and PDF resource library.

## Features

- **Admin Authentication**: JWT-based authentication with Argon2 password hashing
- **Event Management**: Full CRUD operations for events
- **Registration System**: Public event registration with duplicate prevention
- **Resource Library**: PDF upload, download, and management
- **Security**: Rate limiting, input sanitization, security headers, CORS protection
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Authentication**: JWT (PyJWT) + Argon2
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create `.env` file from example:**
   ```bash
   cp .env.example .env
   ```

3. **Update `.env` with your configuration:**
   - Set `JWT_SECRET_KEY` to a secure random string (min 32 characters)
   - Update `FRONTEND_URL` and `ALLOWED_ORIGINS` if needed

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

5. **Seed the database:**
   ```bash
   docker-compose exec backend python scripts/seed_db.py
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   - Create database: `cybersec_club`
   - Update `DATABASE_URL` in `.env`

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Seed database:**
   ```bash
   python scripts/seed_db.py
   ```

5. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Admin login (rate limited: 5/15min)
- `GET /api/auth/me` - Get current user (protected)

### Events

- `GET /api/events` - List all events (public)
- `GET /api/events/{id}` - Get event by ID (public)
- `POST /api/events` - Create event (admin)
- `PUT /api/events/{id}` - Update event (admin)
- `DELETE /api/events/{id}` - Delete event (admin, soft delete)

### Registrations

- `POST /api/registrations` - Register for event (public)
- `GET /api/registrations` - List registrations (admin)
- `GET /api/registrations/{id}` - Get registration (admin)
- `GET /api/registrations/export/csv` - Export CSV (admin)

### Resources

- `GET /api/resources` - List all resources (public)
- `GET /api/resources/{id}` - Get resource (public)
- `GET /api/resources/{id}/download` - Download PDF (public)
- `POST /api/resources` - Upload resource (admin)
- `PUT /api/resources/{id}` - Update resource (admin)
- `DELETE /api/resources/{id}` - Delete resource (admin)

## Authentication

Most endpoints require authentication. To authenticate:

1. **Login:**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Use the token:**
   ```bash
   curl -X GET "http://localhost:8000/api/auth/me" \
     -H "Authorization: Bearer <your-token>"
   ```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (min 32 chars)
- `FRONTEND_URL`: Frontend URL for CORS
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `UPLOAD_DIR`: Directory for PDF storage
- `MAX_FILE_SIZE_MB`: Maximum PDF file size (default: 10MB)

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Security Features

- **Password Hashing**: Argon2 with configurable parameters
- **JWT Tokens**: 1-hour expiration, HS256 algorithm
- **Rate Limiting**: 
  - Login: 5 requests per 15 minutes per IP
  - Admin endpoints: 100 requests per minute
  - General API: 200 requests per minute
- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **Input Sanitization**: XSS prevention using bleach
- **File Validation**: PDF magic bytes verification, size limits
- **CORS**: Configurable origin whitelist

## Testing

Run tests (when implemented):
```bash
pytest
```

## Production Deployment

1. **Set strong `JWT_SECRET_KEY`** in environment
2. **Use environment variables** instead of `.env` file
3. **Configure reverse proxy** (Nginx) with SSL/TLS
4. **Set up database backups**
5. **Configure monitoring and logging**
6. **Review and adjust rate limits** as needed
7. **Set proper file permissions** for uploads directory

## Default Admin Credentials

After seeding:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT**: Change the admin password immediately after first login!

## License

[Your License Here]
