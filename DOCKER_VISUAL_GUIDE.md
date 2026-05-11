# 🐳 Docker Setup - Visual Guide

## 📁 Files Created

```
Pet_AI_Backend/
│
├── 🐳 DOCKER CONFIGURATION
│   ├── Dockerfile.fastapi           ← FastAPI CV Models service
│   ├── Dockerfile.chatbot           ← Chatbot RAG service  
│   ├── docker-compose.yml           ← Orchestrates both services
│   └── .dockerignore                ← Optimizes build context
│
├── 🚀 HELPER SCRIPTS (executable)
│   ├── docker-start.sh              ← Run this first!
│   ├── docker-stop.sh               ← Graceful shutdown
│   └── docker-logs.sh               ← View live logs
│
├── 🔧 CONFIGURATION
│   ├── .env.example                 ← Copy to .env and add keys
│   └── .env                         ← (Create from example)
│
└── 📚 DOCUMENTATION
    ├── DOCKER_README.md             ← Quick reference (START HERE)
    ├── DOCKER_SETUP.md              ← Complete detailed guide
    └── DOCKER_IMPLEMENTATION.md     ← Technical details
```

## 🎯 Quick Start (3 Commands)

```bash
# 1️⃣ Make it executable and run setup
chmod +x docker-start.sh
./docker-start.sh

# 2️⃣ Wait for services to start (~1-2 minutes)
# Script will show you when they're ready

# 3️⃣ Access your services
# FastAPI:  http://localhost:8000/docs
# Chatbot:  http://localhost:8001/docs
```

## 📊 Service Overview

```
┌─────────────────────────────────────────────────┐
│  🐳 FASTAPI SERVICE (Port 8000)                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Dockerfile:  Dockerfile.fastapi                │
│  Image Size:  ~4-5GB (PyTorch-based)           │
│  Base Image:  pytorch/pytorch:2.1.1-runtime    │
│                                                 │
│  🔧 Components:                                 │
│    • Dog Skin Classifier                       │
│    • Dog Eye Classifier                        │
│    • Cat Skin Classifier                       │
│                                                 │
│  📊 API Docs: http://localhost:8000/docs       │
│  🔄 Health:   /health (auto-monitored)         │
│                                                 │
└─────────────────────────────────────────────────┘

         ⬆️ Internal Network ⬇️
    (Docker bridge: pet-ai-network)

┌─────────────────────────────────────────────────┐
│  🤖 CHATBOT SERVICE (Port 8001)                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Dockerfile:  Dockerfile.chatbot                │
│  Image Size:  ~3-4GB (RAG + Docling)           │
│  Base Image:  python:3.11-slim                 │
│                                                 │
│  🔧 Components:                                 │
│    • LangChain Agent                           │
│    • RAG Pipeline                              │
│    • ChromaDB Vector Store                     │
│    • Docling Document Processor                │
│    • Sentence Transformers                     │
│                                                 │
│  📊 API Docs: http://localhost:8001/docs       │
│  🔄 Health:   /health (auto-monitored)         │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 💾 Data Persistence

```
Docker Volumes (Managed by Docker)
│
├── chatbot-db ──────────────────► /app/chatbot/db
│   └─ ChromaDB vector store
│      ✓ Survives container restart
│      ✓ Auto-created if missing
│
├── chatbot-rag-output ──────────► /app/chatbot/rag_output
│   └─ Ingested RAG documents
│      ✓ Persistent
│      ✓ Large files OK
│
└── chatbot-rag-cleaned ────────► /app/chatbot/rag_output_cleaned
    └─ Cleaned/processed documents
       ✓ Persistent
       ✓ Survives updates


Bind Mounts (From Host)
│
├── ./weights ──────────────────► /app/weights (read-only)
│   └─ Your model files
│      ✓ Fast access
│      ✓ Can be updated without rebuild
│
└── ./sample_images ───────────► /app/sample_images (read-only)
    └─ Test images
       ✓ Can update anytime
```

## 🛠️ Usage Commands

```bash
┌─ STARTUP ─────────────────────────────────┐
│ ./docker-start.sh                         │
│  ├─ Checks Docker installation            │
│  ├─ Creates .env if missing              │
│  ├─ Builds images                        │
│  ├─ Starts containers                    │
│  └─ Shows status                         │
└───────────────────────────────────────────┘

┌─ MONITORING ──────────────────────────────┐
│ ./docker-logs.sh [fastapi|chatbot|all]   │
│ docker-compose ps                         │
│ docker stats                              │
│ docker-compose logs -f [service]          │
└───────────────────────────────────────────┘

┌─ CONTROL ─────────────────────────────────┐
│ ./docker-stop.sh           # Stop all     │
│ docker-compose restart     # Restart      │
│ docker-compose restart fastapi  # Restart 1 │
│ docker-compose down -v     # Remove all+data │
└───────────────────────────────────────────┘

┌─ DEBUGGING ───────────────────────────────┐
│ docker exec -it pet-ai-fastapi bash       │
│ docker exec -it pet-ai-chatbot bash       │
│ docker exec pet-ai-chatbot python -c "..." │
│ docker inspect pet-ai-fastapi             │
└───────────────────────────────────────────┘

┌─ CLEANUP ─────────────────────────────────┐
│ docker system prune -a --volumes          │
│ docker volume ls                          │
│ docker volume prune                       │
└───────────────────────────────────────────┘
```

## ✅ Checklist

Before starting, ensure you have:

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose: `docker-compose --version`
- [ ] 8GB+ RAM available
- [ ] 15GB+ free disk space
- [ ] OPENAI_API_KEY ready
- [ ] (Optional) LANGSMITH_API_KEY ready
- [ ] Scripts are executable: `ls -la docker-*.sh`

## 🚀 Step-by-Step Guide

### Step 1: Prepare

```bash
# Navigate to project
cd /Users/akilafernando/Documents/GitHub/Pet_AI_Backend

# Verify files exist
ls -la Dockerfile.* docker-compose.yml docker-*.sh .dockerignore

# All should show ✓
```

### Step 2: Run Setup Script

```bash
./docker-start.sh

# This will:
# 1. Check Docker/Docker Compose
# 2. Create .env file from .env.example
# 3. Open editor for you to add API keys
# 4. Build images (5-10 minutes, happens once)
# 5. Start containers
# 6. Wait for health checks
# 7. Show status
```

### Step 3: Verify Running

```bash
# Check status
docker-compose ps

# Should show:
# NAME              STATUS           PORTS
# pet-ai-fastapi    Up (healthy)     0.0.0.0:8000->8000/tcp
# pet-ai-chatbot    Up (healthy)     0.0.0.0:8001->8001/tcp
```

### Step 4: Test Services

```bash
# Test FastAPI
curl http://localhost:8000/docs
# Should show Swagger UI

# Test Chatbot
curl http://localhost:8001/docs
# Should show Swagger UI
```

### Step 5: Use the Services

```bash
# Check logs
./docker-logs.sh

# Or access UIs:
# FastAPI:  http://localhost:8000/docs
# Chatbot:  http://localhost:8001/docs
```

## 📊 Resource Usage

After startup, resources typically used:

```
FastAPI Container:
  Memory:   1-2GB
  CPU:      10-20% (idle)
  Disk:     5GB (image)

Chatbot Container:
  Memory:   2-3GB
  CPU:      5-10% (idle)
  Disk:     4GB (image)

Named Volumes:
  chatbot-db:     100-500MB
  rag-output:     1-5GB
  rag-cleaned:    500MB-2GB
```

## 🔑 Environment Variables

Must set in `.env`:
```bash
OPENAI_API_KEY=sk-...
```

Optional:
```bash
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=Pet_AI_Backend
LOG_LEVEL=INFO
```

Auto-handled:
```bash
FASTAPI_URL=http://fastapi:8000  # Internal DNS
PYTHONUNBUFFERED=1               # For log streaming
```

## 🎓 Learning Resources

**Quick Start**: DOCKER_README.md  
**Detailed Guide**: DOCKER_SETUP.md  
**Technical Details**: DOCKER_IMPLEMENTATION.md  

## ❓ Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| Port 8000/8001 already in use | Change ports in docker-compose.yml |
| .env file not found | Run: `cp .env.example .env` |
| Services won't start | Check logs: `./docker-logs.sh` |
| Out of memory | Increase Docker resources |
| Docling fails | Rebuild: `docker-compose build --no-cache` |
| Can't connect services | Verify FASTAPI_URL in chatbot env |

## 📞 Help

1. **Check logs**: `./docker-logs.sh`
2. **Read docs**: Start with DOCKER_README.md
3. **Inspect containers**: `docker-compose ps`
4. **Rebuild**: `docker-compose build --no-cache`

## ✨ What You Get

✅ Fully containerized Pet AI Backend  
✅ Two independent services (FastAPI + Chatbot)  
✅ Service auto-discovery via Docker network  
✅ Persistent data across restarts  
✅ Automatic health monitoring  
✅ Easy-to-use helper scripts  
✅ Comprehensive documentation  
✅ Production-ready configuration  

## 🎉 Ready?

```bash
cd /Users/akilafernando/Documents/GitHub/Pet_AI_Backend
./docker-start.sh
```

Then visit:
- **FastAPI**: http://localhost:8000/docs
- **Chatbot**: http://localhost:8001/docs

Happy coding! 🚀
