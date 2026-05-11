# 🐳 Docker Setup - Quick Reference

## TL;DR - Get Started in 3 Steps

```bash
# 1. Create environment file and add your API keys
cp .env.example .env
# Edit .env and add OPENAI_API_KEY and LANGSMITH_API_KEY

# 2. Start everything
./docker-start.sh

# 3. Access your services
# FastAPI: http://localhost:8000/docs
# Chatbot: http://localhost:8001/docs
```

## What's Included

✅ **Dockerfile.fastapi** - CV Models Server  
✅ **Dockerfile.chatbot** - Chatbot & RAG Pipeline  
✅ **docker-compose.yml** - Orchestrates both services  
✅ **.dockerignore** - Optimized build context  
✅ **docker-start.sh** - Automated setup script  
✅ **docker-stop.sh** - Clean shutdown script  
✅ **docker-logs.sh** - View service logs  
✅ **DOCKER_SETUP.md** - Comprehensive guide  

## Architecture

```
Your Host Machine
    ├─ Port 8000 → FastAPI (CV Models)
    │  ├─ Dog Skin Classifier
    │  ├─ Dog Eye Classifier  
    │  └─ Cat Skin Classifier
    │
    └─ Port 8001 → Chatbot Service (RAG)
       ├─ LLM Agent
       ├─ RAG Pipeline
       ├─ ChromaDB Vector Store
       └─ Docling Document Processor
```

## Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| FastAPI | 8000 | CV Model Inference | ✓ Lightweight |
| Chatbot | 8001 | RAG + Agent | ✓ Includes Docling |

## Persistent Volumes

| Volume | Purpose | Location |
|--------|---------|----------|
| `chatbot-db` | ChromaDB vector store | Docker managed |
| `chatbot-rag-output` | RAG documents | Docker managed |
| `chatbot-rag-cleaned` | Cleaned documents | Docker managed |
| `./weights` | Model files | Mounted from host |

## Usage

### Start Services

```bash
# Easiest way (recommended)
./docker-start.sh

# Or manually
docker-compose up -d
```

### View Logs

```bash
./docker-logs.sh                 # All services
./docker-logs.sh fastapi         # FastAPI only
./docker-logs.sh chatbot         # Chatbot only
docker-compose logs -f fastapi   # Manual way
```

### Stop Services

```bash
# Graceful stop (keeps containers)
./docker-stop.sh

# Or manually
docker-compose stop

# Remove everything
docker-compose down

# Remove including volumes (⚠️ deletes data)
docker-compose down -v
```

### Check Status

```bash
docker-compose ps
```

### Access Containers

```bash
# FastAPI shell
docker exec -it pet-ai-fastapi bash

# Chatbot shell  
docker exec -it pet-ai-chatbot bash

# Run Python command
docker exec pet-ai-chatbot python -c "import torch; print('OK')"
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache

# Try again
docker-compose up
```

### Permission Denied on Scripts

```bash
chmod +x docker-start.sh docker-stop.sh docker-logs.sh
```

### Port Already in Use

Edit `docker-compose.yml`:
```yaml
fastapi:
  ports:
    - "8888:8000"  # Change to unused port
```

### Out of Memory/Disk

```bash
# Free up Docker resources
docker system prune -a --volumes

# Check space usage
docker system df
```

### .env File Issues

```bash
# Create from example
cp .env.example .env

# Edit and add keys
nano .env

# Verify keys are set
docker exec pet-ai-chatbot env | grep OPENAI
```

## API Testing

### FastAPI Endpoints

```bash
# Health check
curl http://localhost:8000/docs

# Predict disease
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_images/sample.jpg" \
  -F "animal=dog" \
  -F "disease_type=skin"

# Analyze image (chatbot integration)
curl -X POST "http://localhost:8000/analyze-image" \
  -F "file=@sample_images/sample.jpg" \
  -F "animal=dog" \
  -F "disease_type=skin"
```

### Chatbot Endpoints

Check `http://localhost:8001/docs` for available endpoints

## Resource Requirements

| Aspect | Minimum | Recommended |
|--------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4GB | 8GB+ |
| Disk | 10GB | 20GB+ |
| GPU | Optional | Recommended (CUDA) |

## File Structure

```
Pet_AI_Backend/
├── Dockerfile.fastapi          # FastAPI service
├── Dockerfile.chatbot          # Chatbot service
├── docker-compose.yml          # Service orchestration
├── .dockerignore               # Build optimization
├── docker-start.sh             # Quick start script
├── docker-stop.sh              # Stop script
├── docker-logs.sh              # Logs script
├── .env.example                # Environment template
├── .env                        # (Create from example)
├── DOCKER_SETUP.md             # Detailed guide
│
├── app/                        # FastAPI app
│   ├── main.py
│   ├── models/
│   └── ...
├── chatbot/                    # Chatbot service
│   ├── main.py
│   ├── rag/
│   ├── db/                     # ChromaDB (persistent)
│   └── ...
├── weights/                    # Model files (mounted)
└── requirements.txt            # Python dependencies
```

## Common Commands

```bash
# View everything
docker-compose ps              # Status of all services
docker-compose logs            # Last logs
docker-compose logs -f         # Live logs (Ctrl+C to exit)

# Manage services
docker-compose start           # Start stopped services
docker-compose stop            # Stop running services
docker-compose restart         # Restart all services
docker-compose down            # Stop and remove containers

# Maintenance
docker system df               # Disk usage
docker system prune            # Clean unused resources
docker volume ls               # List volumes
docker logs pet-ai-fastapi     # Get container logs

# Advanced
docker exec pet-ai-fastapi bash          # Shell access
docker inspect pet-ai-chatbot             # Full details
docker stats                              # Live resource usage
```

## Next Steps

1. **Configure environment**: Edit `.env` with your API keys
2. **Start services**: Run `./docker-start.sh`
3. **Test endpoints**: Visit `http://localhost:8000/docs` and `http://localhost:8001/docs`
4. **View logs**: Run `./docker-logs.sh` to debug if needed
5. **Read detailed guide**: See [DOCKER_SETUP.md](DOCKER_SETUP.md) for advanced topics

## Key Features

✨ **Automatic Health Checks** - Services are monitored continuously  
✨ **Service Discovery** - Containers talk to each other via service names  
✨ **Persistent Data** - Volumes survive container restarts  
✨ **Docling Support** - All system dependencies for docling included  
✨ **Hot Logs** - Easy real-time log viewing  
✨ **Quick Scripts** - Bash helper scripts for common tasks  

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

Optional:
- `LANGSMITH_API_KEY` - For LangSmith tracing
- `FASTAPI_URL` - Where chatbot finds FastAPI (default: http://fastapi:8000)
- `LOG_LEVEL` - Logging level (default: INFO)

## Performance Tips

1. **Allocate enough resources**:
   - Docker Desktop → Preferences → Resources
   - 4+ CPU cores, 8+ GB RAM

2. **Use named volumes** (already configured):
   - Faster than bind mounts for large datasets
   - Managed by Docker automatically

3. **Build once, run many**:
   - Images are cached after first build
   - Subsequent `docker-compose up` is instant

## Getting Help

1. Check [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed troubleshooting
2. View service logs: `./docker-logs.sh`
3. Check Docker status: `docker-compose ps`
4. Inspect containers: `docker exec -it pet-ai-chatbot bash`

---

**Ready to go?** Run `./docker-start.sh` 🚀
