#!/bin/bash

# Test runner script for Vectal.ai Clone

set -e

echo "🧪 Running Vectal.ai Clone Test Suite"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${RED}PostgreSQL is not running. Starting...${NC}"
    docker-compose up -d postgres
    sleep 5
fi

# Create test database if it doesn't exist
echo -e "\n${YELLOW}Setting up test database...${NC}"
docker-compose exec -T postgres psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'vectal_test'" | grep -q 1 || \
    docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE vectal_test"

# Parse command line arguments
TEST_PATH="${1:-tests/}"
COVERAGE="${2:-}"

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
if [ "$COVERAGE" = "--coverage" ]; then
    echo "Running with coverage report..."
    pytest "$TEST_PATH" --cov=. --cov-report=html --cov-report=term-missing -v
    echo -e "\n${GREEN}Coverage report generated in htmlcov/index.html${NC}"
else
    pytest "$TEST_PATH" -v
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi
