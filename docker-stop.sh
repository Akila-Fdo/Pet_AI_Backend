#!/bin/bash

# Pet AI Backend - Docker Stop Script
# Safely stops all services and cleans up

echo "Stopping Pet AI Backend services..."
echo ""

docker-compose down

echo ""
echo "✓ Services stopped and containers removed"
echo ""
echo "Note: Docker volumes (persistent data) are preserved"
echo "To also delete volumes, run: docker-compose down -v"
