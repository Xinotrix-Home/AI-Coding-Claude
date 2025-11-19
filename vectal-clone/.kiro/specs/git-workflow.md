# Git Workflow Specification

## Branch Naming Convention

**Format:** `feature/<feature-name>`

**Examples:**
- `feature/authentication-tests`
- `feature/task-management-tests`
- `feature/project-organization`
- `feature/ai-chat-system`

**Rules:**
- One branch per phase/major feature
- No phase numbers in branch names
- Use kebab-case
- Keep names descriptive but concise

---

## Commit Strategy

### 1. Module-wise commits within feature branch

Break down work into logical modules/submodules:

```
feature/authentication-tests
├── commit: "test: add pytest infrastructure and fixtures"
├── commit: "test: add password and JWT unit tests"
├── commit: "test: add registration and login integration tests"
├── commit: "test: add OAuth integration tests"
└── commit: "test: add security and rate limiting tests"
```

### 2. Merge to main with summary

```bash
git checkout main
git merge feature/authentication-tests --no-ff
```

---

## Commit Message Format

**Format:** `<type>: <description>`

**Types:**
- `feat:` - New feature
- `test:` - Adding tests
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `ci:` - CI/CD changes

**Rules:**
- Write as a developer (no AI/Kiro attribution)
- Be concise and descriptive
- Use present tense ("add" not "added")
- Start with lowercase after colon

**Good Examples:**
```
test: add authentication unit tests
feat: implement task recurrence logic
docs: update quick start guide
ci: configure GitHub Actions workflow
```

**Bad Examples:**
```
Added tests with Kiro's help
Kiro implemented authentication
AI-generated test suite
```

---

## Current Work Commits

### Branch: `feature/authentication-tests`

```bash
git checkout -b feature/authentication-tests

# Commit 1: Infrastructure
git add backend/tests/__init__.py backend/tests/conftest.py backend/pytest.ini backend/run_tests.sh
git commit -m "test: add pytest infrastructure and fixtures"

# Commit 2: Unit tests
git add backend/tests/unit/
git commit -m "test: add password and JWT unit tests"

# Commit 3: Integration tests
git add backend/tests/integration/test_auth_*.py
git commit -m "test: add authentication integration tests"

# Commit 4: CI/CD
git add backend/requirements.txt .github/workflows/test.yml
git commit -m "ci: add test dependencies and GitHub Actions"

# Commit 5: Docs
git add backend/tests/README.md backend/tests/PHASE2_COMPLETION.md
git commit -m "docs: add authentication test documentation"

# Merge
git checkout main
git merge feature/authentication-tests --no-ff
```

### Branch: `feature/task-management-tests`

```bash
git checkout -b feature/task-management-tests

# Commit 1: Unit tests
git add backend/tests/unit/test_recurrence.py
git commit -m "test: add recurrence utility unit tests"

# Commit 2: Integration tests
git add backend/tests/integration/test_tasks.py
git commit -m "test: add task management integration tests"

# Merge
git checkout main
git merge feature/task-management-tests --no-ff
```

### Branch: `feature/project-documentation`

```bash
git checkout -b feature/project-documentation

# Commit 1: All docs
git add DEVELOPMENT_STATUS.md SESSION_SUMMARY.md QUICK_START.md README.md
git commit -m "docs: add project documentation and status tracking"

# Merge
git checkout main
git merge feature/project-documentation --no-ff
```

---

## Quick Reference

```bash
# Create feature branch
git checkout -b feature/<name>

# Stage and commit module
git add <files>
git commit -m "<type>: <description>"

# Merge to main
git checkout main
git merge feature/<name> --no-ff

# Push
git push origin main
```
