# Vectal.ai Clone - AI-Powered Productivity Platform

A comprehensive AI-powered productivity platform inspired by Vectal.ai, featuring task management, AI chat, notes, projects, calendar integration, and more.

## 🚀 Features

- **AI Chat Agent** - Natural language interaction with GPT-4
- **Task Management** - Smart task organization with priorities and due dates
- **Notes System** - Markdown notes with bidirectional linking
- **Project Organization** - Hierarchical project structure
- **Calendar Integration** - Google Calendar sync
- **Memory & Context** - Persistent AI memory across sessions
- **Workflow Automation** - Custom workflows with triggers and actions
- **Image Generation** - DALL-E 3 integration for visual assets
- **MCP Server** - IDE integration (VS Code, Cursor, Windsurf)
- **Gamification** - Streaks, leaderboards, and achievements
- **Real-time Collaboration** - WebSocket-based live updates
- **Analytics Dashboard** - Productivity insights and trends

## 🏗️ Architecture

### Backend
- **FastAPI** (Python 3.11+) - High-performance async API
- **PostgreSQL 15** - Relational data (users, tasks, projects)
- **MongoDB 7.0** - Document store (chat, notes, memories)
- **Redis 7.0** - Caching and real-time pub/sub
- **Qdrant** - Vector database for semantic search
- **Celery** - Background task processing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Shadcn/ui** - Component library
- **React Query** - Server state management

### AI/ML
- **OpenAI GPT-4** - Language model
- **DALL-E 3** - Image generation
- **LangChain** - LLM orchestration
- **Sentence Transformers** - Embeddings

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Git

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd vectal-ai-clone
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- FastAPI backend on `http://localhost:8000`
- Next.js frontend on `http://localhost:3000`
- PostgreSQL on `localhost:5432`
- MongoDB on `localhost:27017`
- Redis on `localhost:6379`
- Qdrant on `localhost:6333`

### 4. Run database migrations

```bash
docker-compose exec api alembic upgrade head
```

### 5. Access the application

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc

## 📁 Project Structure

```
vectal-ai-clone/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   ├── db/                 # Database configuration
│   ├── utils/              # Utility functions
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker image
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── lib/                # Utility libraries
│   ├── types/              # TypeScript types
│   ├── package.json        # Node dependencies
│   └── Dockerfile          # Frontend Docker image
├── nginx/                  # Nginx configuration
│   └── nginx.conf          # Reverse proxy config
├── docker-compose.yml      # Docker services
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔑 Environment Variables

See `.env.example` for all required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key for GPT-4 and DALL-E
- `JWT_SECRET` - Secret key for JWT tokens
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Run All Tests
```bash
cd backend
./run_tests.sh
```

### Run with Coverage
```bash
cd backend
./run_tests.sh tests/ --coverage
```

### Unit Tests
```bash
cd backend
pytest tests/unit -v
```

### Integration Tests
```bash
cd backend
pytest tests/integration -v
```

### Specific Test File
```bash
cd backend
pytest tests/integration/test_auth_login.py -v
```

### Test Coverage
- ✅ Password hashing and validation
- ✅ JWT token management
- ✅ User registration and login
- ✅ OAuth authentication (Google, GitHub)
- ✅ Rate limiting and account lockout
- ✅ Security features

See `backend/tests/README.md` for detailed testing documentation.

## 🚢 Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Vectal.ai](https://vectal.ai)
- Built with FastAPI, Next.js, and OpenAI

## 📊 Project Status

**Current Progress:** 3/20 phases complete (15%)
- ✅ Phase 1: Project Setup and Infrastructure
- ✅ Phase 2: Authentication System (100% test coverage)
- ✅ Phase 3: Task Management System (100% test coverage)

**Test Coverage:** 96% (100+ tests)

For detailed status, see:
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Development Status:** [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md)
- **Session Summary:** [SESSION_SUMMARY.md](SESSION_SUMMARY.md)
- **Test Documentation:** [backend/tests/README.md](backend/tests/README.md)

## 📧 Contact

For questions or support, please open an issue on GitHub.
