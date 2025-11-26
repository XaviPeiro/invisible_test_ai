We will develop an 3 components application: the backend, the frontend and the infrastructure definitions (IAC, mainly with Terraform).

We'll be taking one part at once.

Let's start planning the backend. I will be provinding the different features.

# BACKEND
1. Python Backend Service using a SQL database.
    1. API supporting the behaviors.

# BEHAVIOUR
1. User sign up
2. Authentication for existing user
3. User profile management
4. View user’s groups
5. Group management
  a. Add group
  b. Add user to group as member
6. Expense management
  a. Add expense for group (paying user and amount + any metadata)
  b. View expense history
  c. Summarize balance by amount owed to members (assuming equal share in each
  expense)

---

## BACKEND ARCHITECTURE PLAN

### Technology Stack (Pending Confirmation)
- **Web Framework**: FastAPI (lightweight, async, auto-docs) or Flask (simpler, more traditional)
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Database Migrations**: Alembic
- **Password Hashing**: bcrypt or passlib
- **Validation**: Pydantic (if FastAPI) or marshmallow (if Flask)
- **Testing**: pytest
- **Containerization**: Docker + Docker Compose

**Question**: Do you prefer FastAPI or Flask? FastAPI provides automatic OpenAPI docs and async support, while Flask is more minimal.

### Architecture Overview (OOP-based)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session management
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── user.py             # User model
│   │
│   ├── schemas/                # Pydantic/marshmallow schemas (request/response)
│   │   ├── __init__.py
│   │   └── user.py             # User schemas (SignUpRequest, UserResponse)
│   │
│   ├── services/               # Business logic layer (OOP)
│   │   ├── __init__.py
│   │   └── user_service.py     # UserService class
│   │
│   ├── repositories/           # Data access layer (OOP)
│   │   ├── __init__.py
│   │   └── user_repository.py  # UserRepository class
│   │
│   └── api/                    # API routes/endpoints
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           └── auth.py         # Authentication endpoints (signup, etc.)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   └── test_user_signup.py     # User signup tests
│
├── alembic/                    # Database migrations
│   └── versions/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Database Schema

**User Table:**
- `id` (UUID or Integer, Primary Key)
- `email` (String, Unique, Not Null)
- `username` (String, Unique, Not Null) - Optional
- `password_hash` (String, Not Null)
- `created_at` (DateTime, Not Null)
- `updated_at` (DateTime, Not Null)
- `is_active` (Boolean, Default: True)

### API Design

**POST /api/auth/signup**
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "username": "username",  // Optional
    "password": "secure_password"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "created_at": "2024-01-01T00:00:00Z"
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Validation errors (invalid email, weak password, etc.)
  - `409 Conflict`: Email/username already exists

### Service Layer Design (OOP)

**UserService Class:**
- `signup(email, password, username=None) -> User`
- `validate_email(email) -> bool`
- `validate_password(password) -> bool`
- `hash_password(password) -> str`

**UserRepository Class:**
- `create(user_data) -> User`
- `find_by_email(email) -> User | None`
- `find_by_username(username) -> User | None`
- `exists_by_email(email) -> bool`

### Docker Setup

- **Backend Service**: Python container
- **Database**: PostgreSQL container
- **Network**: Docker network for service communication
- **Volumes**: Database persistence, code volume mount for development

### Next Steps
1. Confirm technology choices (FastAPI vs Flask)
2. Set up project structure
3. Implement database models
4. Implement repository layer
5. Implement service layer
6. Implement API endpoints
7. Add tests
8. Create Docker configuration
