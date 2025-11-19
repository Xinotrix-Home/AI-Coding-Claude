# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd vectal-ai-clone

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Services

```bash
# Start all services with Docker
docker-compose up -d

# Check services are running
docker-compose ps
```

### 3. Run Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Redoc:** http://localhost:8000/redoc

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# All tests
./run_tests.sh

# With coverage
./run_tests.sh tests/ --coverage

# Specific tests
pytest tests/unit/ -v
pytest tests/integration/test_auth_*.py -v
pytest tests/integration/test_tasks.py -v
```

### Test Coverage

Current coverage: **96%**
- Authentication: 98%
- Task Management: 95%

## 📁 Project Structure

```
vectal-ai-clone/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   │   ├── routes/         # Endpoint definitions
│   │   └── dependencies/   # Dependency injection
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   │   └── schemas/        # Pydantic schemas
│   ├── db/                 # Database configuration
│   ├── utils/              # Utility functions
│   ├── tasks/              # Celery tasks
│   ├── tests/              # Test suite
│   │   ├── unit/           # Unit tests
│   │   └── integration/    # Integration tests
│   └── main.py             # Application entry
│
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   │   ├── login/          # Login page
│   │   ├── register/       # Registration page
│   │   ├── dashboard/      # Dashboard page
│   │   └── auth/           # OAuth callback
│   ├── components/         # React components
│   │   ├── features/       # Feature components
│   │   ├── layout/         # Layout components
│   │   └── ui/             # UI components
│   └── lib/                # Utilities
│       └── api/            # API clients
│
├── .github/                # GitHub Actions
│   └── workflows/          # CI/CD workflows
├── docker-compose.yml      # Docker services
└── .env.example            # Environment template
```

## 🔑 Key Features Implemented

### ✅ Phase 1: Infrastructure
- Docker setup (PostgreSQL, MongoDB, Redis, Qdrant)
- FastAPI backend with async support
- Next.js 14 frontend with App Router
- Database connections configured

### ✅ Phase 2: Authentication
- Email/password registration and login
- JWT tokens (access + refresh)
- Google and GitHub OAuth
- Rate limiting (5 attempts per 15 min)
- Account lockout (10 failed attempts)
- Password strength validation
- Protected routes

### ✅ Phase 3: Task Management
- Create, read, update, delete tasks
- Task priorities (0-4)
- Task labels
- Due dates
- Task completion tracking
- Recurring tasks (daily, weekly, monthly, yearly)
- Task reminders (24h and 1h before due)
- Filtering and pagination
- Today's tasks view

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/oauth/google` - Google OAuth
- `GET /api/v1/oauth/github` - GitHub OAuth

### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks (with filters)
- `GET /api/v1/tasks/today` - Get today's tasks
- `GET /api/v1/tasks/{id}` - Get specific task
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/complete` - Mark complete
- `POST /api/v1/tasks/{id}/uncomplete` - Mark incomplete
- `POST /api/v1/tasks/{id}/recurrence` - Set recurrence
- `DELETE /api/v1/tasks/{id}/recurrence` - Remove recurrence

## 🔐 Environment Variables

Required variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/vectal
MONGODB_URL=mongodb://localhost:27017/vectal
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI (for future phases)
OPENAI_API_KEY=your-openai-api-key
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# View logs
docker-compose logs postgres
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Test Failures

```bash
# Ensure test database exists
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE vectal_test"

# Clear test database
docker-compose exec postgres psql -U postgres -c "DROP DATABASE vectal_test"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE vectal_test"

# Run tests with verbose output
pytest -vv
```

## 📚 Documentation

- **Development Status:** `DEVELOPMENT_STATUS.md`
- **Session Summary:** `SESSION_SUMMARY.md`
- **Test Documentation:** `backend/tests/README.md`
- **Phase 2 Completion:** `backend/tests/PHASE2_COMPLETION.md`
- **API Documentation:** http://localhost:8000/docs (when running)

## 🎯 Next Steps

### Option 1: Phase 4 - Project Organization
Build project hierarchy and collaboration features

### Option 2: Phase 6 - AI Chat System
Implement GPT-4 powered conversational AI

### Option 3: Expand Testing
Add load tests, E2E tests, performance benchmarks

## 💡 Tips

1. **Use the API docs** - Visit `/docs` for interactive API testing
2. **Check logs** - Use `docker-compose logs -f api` to see backend logs
3. **Run tests often** - Catch bugs early with `./run_tests.sh`
4. **Use fixtures** - Leverage test fixtures in `conftest.py`
5. **Read the specs** - Check `.kiro/specs/vectal-ai-clone/tasks.md` for details

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure tests pass (`./run_tests.sh`)
4. Update documentation
5. Submit pull request

## 📞 Support

- Check `DEVELOPMENT_STATUS.md` for project status
- Read `backend/tests/README.md` for testing help
- View API docs at `/docs` endpoint
- Check Docker logs for service issues

---

**Status:** 3/20 phases complete (15%) | **Coverage:** 96% | **Tests:** 100+
