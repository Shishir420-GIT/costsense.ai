#!/bin/bash

echo "=== CostSense AI Structure Verification ==="
echo ""

# Check directories
echo "📁 Checking directory structure..."
for dir in backend frontend infra; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ missing"
    fi
done
echo ""

# Check backend files
echo "📁 Checking backend files..."
for file in backend/pyproject.toml backend/Dockerfile backend/.env.example backend/app/main.py backend/app/config.py; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done
echo ""

# Check frontend files
echo "📁 Checking frontend files..."
for file in frontend/package.json frontend/Dockerfile frontend/vite.config.ts frontend/src/App.tsx; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done
echo ""

# Check infra files
echo "📁 Checking infra files..."
for file in infra/Dockerfile.ollama; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done
echo ""

# Check root files
echo "📁 Checking root files..."
for file in docker-compose.yml README.md .gitignore; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done
echo ""

echo "=== Phase 1 Complete! ==="
echo ""
echo "Next steps:"
echo "1. Install Docker and Docker Compose"
echo "2. Run: docker-compose up -d"
echo "3. Access frontend at: http://localhost"
echo "4. Access API docs at: http://localhost:8000/docs"
