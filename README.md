# Invisible - Expense Sharing Application

A 3-component application for expense sharing between groups of users.

## Components

- **Backend**: Django REST Framework API with PostgreSQL
- **Frontend**: (Coming soon)
- **Infrastructure**: (Coming soon - Terraform)

## Backend

### Technology Stack

- Python 3.12
- Django 5.0 + Django REST Framework
- PostgreSQL 16
- pytest for testing
- Docker & Docker Compose

### Quick Start (Docker)

1. From the project root, start the application:
   ```bash
   docker-compose up --build
   ```

2. The API will be available at `http://localhost:8000`

### API Endpoints

#### User Sign Up

```
POST /api/auth/signup/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "optional_username"
}
```

**Success Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "optional_username",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors (invalid email, weak password)
- `409 Conflict`: Email or username already exists

#### User Login

```
POST /api/auth/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "optional_username",
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors (missing fields, invalid email format)
- `401 Unauthorized`: Invalid email or password

**Using the Access Token:**
Include the access token in the Authorization header for protected endpoints:
```
Authorization: Bearer <access_token>
```

#### User Profile Management

```
GET /api/auth/profile/
PUT /api/auth/profile/
PATCH /api/auth/profile/
```

**Get Profile (GET):**
- Requires authentication
- Returns current user's profile information

**Update Profile (PUT/PATCH):**
- Requires authentication
- Request Body (all fields optional):
```json
{
  "email": "newemail@example.com",
  "username": "newusername"
}
```

**Success Response (200):**
```json
{
  "id": "uuid",
  "email": "newemail@example.com",
  "username": "newusername",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors (invalid email format)
- `401 Unauthorized`: Not authenticated
- `409 Conflict`: Email or username already exists

#### Change Password

```
POST /api/auth/profile/change-password/
```

**Request Body:**
```json
{
  "old_password": "currentpassword123",
  "new_password": "newpassword123"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully."
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors (weak password, missing fields)
- `401 Unauthorized`: Invalid old password or not authenticated

### Running Tests

With Docker (from project root):
```bash
docker-compose exec backend pytest
```

Or locally (requires PostgreSQL):
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Development

For local development without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (or create a `.env` file):
   ```bash
   export DB_HOST=localhost
   export DB_NAME=invisible_db
   export DB_USER=postgres
   export DB_PASSWORD=postgres
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## License

MIT

