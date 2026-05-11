# Docker Setup Guide for Pet AI Backend

This guide explains how to run the entire Pet AI Backend project using Docker and Docker Compose.

## Project Architecture

```
┌─────────────────────────────────────────────┐
│         Pet AI Backend Services             │
├─────────────────────────────────────────────┤
│                                             │
│  FastAPI Server (Port 8000)                │
│  ├─ Dog Skin Model                         │
│  ├─ Dog Eye Model                          │
│  └─ Cat Skin Model                         │
│                                             │
│          ↑↓ Internal Network                │
│          (pet-ai-network)                   │
│                                             │
│  Chatbot Service (Port 8001)               │
│  ├─ LLM Agent                              │
│  ├─ RAG Pipeline                           │
│  ├─ ChromaDB Vector Store                  │
│  └─ Docling Document Processing            │
│                                             │
└─────────────────────────────────────────────┘
```

## Prerequisites

- Docker 20.10+ 
- Docker Compose 2.0+
- At least 8GB RAM available
- ~10GB disk space (models + dependencies)

## Setup Instructions

### 1. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
LANGSMITH_API_KEY=your-langsmith-key-here
```

### 2. Build Docker Images

```bash
# Build both services
docker-compose build

# Or build specific service
docker-compose build fastapi    # Just CV models
docker-compose build chatbot    # Just chatbot
```

### 3. Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Or start in foreground (useful for debugging)
docker-compose up
```

### 4. Verify Services Are Running

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f fastapi   # FastAPI logs
docker-compose logs -f chatbot   # Chatbot logs
docker-compose logs -f           # All logs
```

### 5. Test the Services

**FastAPI Service (http://localhost:8000):**
```bash
# Access API documentation
open http://localhost:8000/docs

# Or test with curl
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_image.jpg" \
  -F "animal=dog" \
  -F "disease_type=skin"
```

**Chatbot Service (http://localhost:8001):**
```bash
# Access chatbot API documentation
open http://localhost:8001/docs

# Or test with curl (check actual endpoints in chatbot/main.py)
curl http://localhost:8001/health
```

## Volume Management

The setup uses Docker volumes for persistent data:

### Named Volumes (Managed by Docker)
- **chatbot-db**: ChromaDB vector store
- **chatbot-rag-output**: RAG documents and ingestion output
- **chatbot-rag-cleaned**: Cleaned documents

### Bind Mounts (Local Filesystem)
- **weights/**: Model weights (read-only in containers)
- **sample_images/**: Test images

### Viewing Persistent Data

```bash
# List all volumes
docker volume ls

# Inspect a volume
docker volume inspect pet_ai_backend_chatbot-db

# Access volume data through running container
docker run -v pet_ai_backend_chatbot-db:/data ubuntu ls -la /data
```

## Common Operations

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart fastapi
```

### View Logs

```bash
# Real-time logs (all services)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service, last 50 lines
docker-compose logs --tail=50 chatbot
```

### Stop Services

```bash
# Stop all services (keeps containers and data)
docker-compose stop

# Stop specific service
docker-compose stop chatbot

# Remove containers (keeps volumes)
docker-compose down

# Remove everything including volumes (⚠️ deletes data!)
docker-compose down -v
```

### Access Container Shell

```bash
# FastAPI container
docker exec -it pet-ai-fastapi bash

# Chatbot container
docker exec -it pet-ai-chatbot bash

# Run Python in container
docker exec -it pet-ai-chatbot python3 -c "import torch; print(torch.cuda.is_available())"
```

## Debugging

### Check Service Health

```bash
# View health status
docker-compose ps

# Check specific service health
docker inspect pet-ai-fastapi | grep -A 5 "Health"
```

### View Full Logs

```bash
# Fetch all logs for a service
docker-compose logs chatbot > chatbot-logs.txt

# View with timestamps
docker-compose logs --timestamps chatbot
```

### Check Resource Usage

```bash
# View Docker container stats
docker stats

# Specific container
docker stats pet-ai-chatbot
```

### If Services Won't Start

1. **Check logs first**:
   ```bash
   docker-compose logs chatbot
   docker-compose logs fastapi
   ```

2. **Verify environment variables**:
   ```bash
   docker exec pet-ai-chatbot env | grep OPENAI
   ```

3. **Test container manually**:
   ```bash
   docker-compose run --rm chatbot python -c "import docling; print('Docling OK')"
   ```

4. **Rebuild from scratch**:
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose build --no-cache
   docker-compose up
   ```

## Network Communication

Services communicate internally using the `pet-ai-network` bridge:

- **FastAPI is accessible to chatbot as**: `http://fastapi:8000`
- This is automatically set via `FASTAPI_URL` environment variable
- From your host machine: `http://localhost:8000` and `http://localhost:8001`

## Performance Tips

1. **Allocate sufficient Docker resources**:
   - Docker Desktop → Preferences → Resources
   - CPU: At least 4 cores
   - Memory: At least 8GB
   - Swap: 2GB+

2. **Use build cache**:
   - Don't use `--no-cache` unless necessary
   - Layers are cached and speed up rebuilds

3. **Monitor resource usage**:
   ```bash
   docker stats
   ```

## Troubleshooting Common Issues

### Docling Installation Fails
If you see errors about `libxml2` or `libxslt1`:
- Dockerfile.chatbot includes all required system dependencies
- Ensure you're building without `--no-cache`: `docker-compose build`

### Model Files Not Found
- Verify `weights/` directory exists on host
- Check volume mounts in `docker-compose.yml`
- Access container and verify: `docker exec pet-ai-fastapi ls -la /app/weights`

### Chatbot Can't Connect to FastAPI
- Ensure FastAPI is healthy: `docker-compose ps`
- Check service name matches: should be `fastapi` (from docker-compose)
- Verify `FASTAPI_URL=http://fastapi:8000` in environment

### Out of Disk Space
```bash
# Clean up unused Docker resources
docker system prune -a --volumes
```

### Port Already in Use
Change ports in `docker-compose.yml`:
```yaml
fastapi:
  ports:
    - "8888:8000"  # External:Internal
```

## Production Considerations

For production deployment:

1. **Use environment-specific compose files**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

2. **Set resource limits** in docker-compose.yml:
   ```yaml
   services:
     fastapi:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

3. **Use health checks** (already included)

4. **Consider using an orchestrator** (Kubernetes) for multiple instances

5. **Separate sensitive data** using Docker secrets

## Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes (careful!)
docker volume prune

# Full cleanup (careful!)
docker system prune -a --volumes
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PyTorch Docker Images](https://hub.docker.com/r/pytorch/pytorch)
