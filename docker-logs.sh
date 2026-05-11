#!/bin/bash

# Pet AI Backend - Docker Logs Script
# Shows real-time logs from all services

set -e

if [ "$1" == "fastapi" ]; then
    echo "📋 FastAPI Logs (Ctrl+C to exit)..."
    docker-compose logs -f fastapi
elif [ "$1" == "chatbot" ]; then
    echo "📋 Chatbot Logs (Ctrl+C to exit)..."
    docker-compose logs -f chatbot
elif [ "$1" == "all" ] || [ -z "$1" ]; then
    echo "📋 All Services Logs (Ctrl+C to exit)..."
    docker-compose logs -f
else
    echo "Usage: $0 [fastapi|chatbot|all]"
    exit 1
fi
