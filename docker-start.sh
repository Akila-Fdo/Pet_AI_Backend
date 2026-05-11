#!/bin/bash

# Pet AI Backend Docker Quick Start Script
# This script automates the initial setup

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Pet AI Backend - Docker Quick Start Setup               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker $(docker --version | awk '{print $3}')"
echo "✓ Docker Compose $(docker-compose --version | awk '{print $3}')"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - LANGSMITH_API_KEY (optional)"
        echo ""
        read -p "Press Enter to open .env in your editor (or Ctrl+C to skip)..."
        ${EDITOR:-nano} .env
    else
        echo "❌ .env.example not found!"
        exit 1
    fi
else
    echo "✓ .env file already exists"
fi

echo ""
echo "🔨 Building Docker images..."
echo "   This may take 5-10 minutes on first run..."
docker-compose build

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "🚀 Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    echo ""
    echo "⏳ Waiting for services to start (this takes ~30 seconds)..."
    sleep 10
    
    # Check services
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "✓ All services started successfully!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "🎉 Setup Complete! Your services are running:"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📍 FastAPI Server (CV Models):"
    echo "   URL: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo ""
    echo "📍 Chatbot Service (RAG Agent):"
    echo "   URL: http://localhost:8001"
    echo "   Docs: http://localhost:8001/docs"
    echo ""
    echo "📋 Useful Commands:"
    echo "   docker-compose logs -f              # View live logs"
    echo "   docker-compose logs -f fastapi      # FastAPI logs only"
    echo "   docker-compose logs -f chatbot      # Chatbot logs only"
    echo "   docker-compose ps                   # Check service status"
    echo "   docker-compose stop                 # Stop services"
    echo "   docker-compose down                 # Stop & remove containers"
    echo ""
    echo "📚 For more details, see: DOCKER_SETUP.md"
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
