# Vectal Clone - AI-Powered Task Management Platform

## 🚀 Deploy Your Own

**👉 [STEP-BY-STEP DEPLOYMENT GUIDE](./DEPLOY-STEP-BY-STEP.md)** ← Click here to deploy!

Or go directly to: [Vercel Dashboard](https://vercel.com/new) | [Full Deployment Docs](./DEPLOYMENT.md)

---

A full-featured clone of Vectal.ai built with Next.js, React, TypeScript, and OpenAI integration. This platform provides intelligent task management, AI-powered chat assistance, notes system, and comprehensive analytics.

## Features

### Core Features
- **AI-Powered Task Management**: Create, organize, and prioritize tasks with intelligent AI assistance
- **Smart Chat Assistant**: Get help with brainstorming, task breakdown, and productivity advice
- **Notes System**: Create and manage notes with tagging and full-text search
- **Analytics Dashboard**: Track your productivity with detailed charts and insights
- **User Authentication**: Secure sign-up and login system with session management

### AI Capabilities
- Automatic task prioritization using GPT-4
- AI-powered task suggestions and breakdown
- Conversational AI assistant for productivity help
- Multiple AI model support (GPT-4, GPT-3.5)

### User Interface
- Modern, responsive design with Tailwind CSS
- Dark mode support
- Mobile-friendly interface
- Real-time updates
- Intuitive navigation with sidebar

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript
- **Styling**: Tailwind CSS
- **Database**: SQLite with Prisma ORM
- **Authentication**: NextAuth.js
- **AI Integration**: OpenAI API
- **Charts**: Recharts
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vectal-clone
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following:
```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL="file:./dev.db"
NEXTAUTH_SECRET="your-secret-key-here"
NEXTAUTH_URL="http://localhost:3000"
```

4. Initialize the database:
```bash
node -e "const Database = require('better-sqlite3'); const db = new Database('prisma/dev.db'); const fs = require('fs'); const sql = fs.readFileSync('scripts/init-db.sql', 'utf8'); sql.split(';').filter(s => s.trim()).forEach(statement => { try { db.exec(statement); } catch(e) { console.log('Skipping:', e.message); } }); db.close(); console.log('Database initialized!');"
```

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Creating an Account

1. Navigate to the homepage
2. Click "Get Started" or "Sign Up"
3. Fill in your details (name, email, password)
4. You'll be automatically logged in and redirected to the dashboard

### Managing Tasks

1. Go to the "Tasks" section from the sidebar
2. Click "New Task" to create a task
3. Fill in task details:
   - Title (required)
   - Description (optional)
   - Priority (low, medium, high, urgent)
   - Due date (optional)
   - Tags (optional)
4. Use the "Get AI help" button to get AI suggestions for task breakdown
5. Filter tasks by status, priority, or search
6. Click on a task to edit or mark as complete
7. Use the "Clear Completed" button to remove completed tasks

### Using the AI Chat

1. Navigate to "AI Chat" from the sidebar
2. Type your question or request
3. Select the AI model (GPT-4 or GPT-3.5)
4. Use quick prompts for common questions:
   - Task prioritization help
   - Project breakdown
   - Productivity tips
   - Time management advice

### Taking Notes

1. Go to the "Notes" section
2. Click the "+" button to create a new note
3. Add a title, content, and tags
4. Notes are automatically saved
5. Search notes using the search bar
6. Click on any note to edit or delete it

### Viewing Analytics

1. Access the "Analytics" section
2. View key metrics:
   - Total tasks and completion rate
   - Task status breakdown
   - Tasks by priority distribution
   - Activity over time
3. Analyze productivity insights and patterns

## Project Structure

```
vectal-clone/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── auth/         # Authentication endpoints
│   │   ├── tasks/        # Task management endpoints
│   │   ├── notes/        # Notes endpoints
│   │   ├── chat/         # Chat endpoints
│   │   └── register/     # User registration
│   ├── dashboard/        # Dashboard page
│   ├── tasks/            # Tasks management page
│   ├── notes/            # Notes page
│   ├── chat/             # AI chat page
│   ├── analytics/        # Analytics page
│   ├── login/            # Login page
│   └── register/         # Registration page
├── components/            # Reusable React components
│   ├── Sidebar.tsx       # Navigation sidebar
│   ├── TaskItem.tsx      # Individual task component
│   └── CreateTaskModal.tsx # Task creation modal
├── lib/                   # Utility functions and configurations
│   ├── prisma.ts         # Prisma client
│   ├── auth.ts           # NextAuth configuration
│   └── openai.ts         # OpenAI integration
├── prisma/               # Database schema and migrations
│   ├── schema.prisma     # Prisma schema
│   └── dev.db            # SQLite database
├── scripts/              # Utility scripts
│   └── init-db.sql       # Database initialization
└── types/                # TypeScript type definitions
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/auth/[...nextauth]` - NextAuth authentication

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PATCH /api/tasks/[id]` - Update task
- `DELETE /api/tasks/[id]` - Delete task
- `POST /api/tasks/prioritize` - AI-powered task prioritization

### Notes
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create new note
- `PATCH /api/notes/[id]` - Update note
- `DELETE /api/notes/[id]` - Delete note

### Chat
- `GET /api/chat` - Get chat history
- `POST /api/chat` - Send message and get AI response
- `DELETE /api/chat` - Clear chat history

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `NEXTAUTH_SECRET` | Secret for NextAuth sessions | Yes |
| `NEXTAUTH_URL` | Application URL | Yes |

## Features in Detail

### Task Management
- Create, read, update, and delete tasks
- Set priority levels (low, medium, high, urgent)
- Add due dates and tags
- Filter by status and priority
- Search functionality
- AI-powered task suggestions

### AI Integration
- GPT-4 and GPT-3.5 support
- Task prioritization based on AI analysis
- Contextual chat assistance
- Task breakdown suggestions
- Productivity recommendations

### Analytics
- Task completion rate tracking
- Time-series analysis of task creation and completion
- Priority distribution visualization
- Status breakdown charts
- Productivity insights

## Security

- Passwords are hashed using bcrypt
- Session-based authentication with NextAuth
- Protected API routes requiring authentication
- CSRF protection
- SQL injection prevention with Prisma

## Performance Optimizations

- Server-side rendering with Next.js
- Automatic code splitting
- Optimized images
- Caching strategies
- Efficient database queries with Prisma

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

This is a demonstration project. Feel free to fork and modify for your own use.

## License

MIT License - feel free to use this project for learning and development purposes.

## Acknowledgments

- Inspired by [Vectal.ai](https://vectal.ai)
- Built with Next.js and OpenAI
- UI components styled with Tailwind CSS

## Support

For issues or questions, please open an issue in the repository.

## Roadmap

Future enhancements could include:
- [ ] Real-time collaboration
- [ ] Mobile apps (iOS/Android)
- [ ] Google Calendar integration
- [ ] Team workspaces
- [ ] Advanced AI models (Claude, DeepSeek, Grok)
- [ ] Dark mode
- [ ] Email notifications
- [ ] Recurring tasks
- [ ] Task templates
- [ ] Export functionality (PDF, CSV)

---

Built with ❤️ using Next.js and OpenAI
