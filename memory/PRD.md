# Proto - AI Frontend Code Generator with RAG Training Pipeline

## Problem Statement
Build a full-stack website based on PDF document about "Project Proto" (Idea into Project). Website allows users to upload an image + text details to generate frontend code using AI. Uses RAG training pipeline with public dataset.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI (dark neon theme)
- **Backend**: FastAPI + MongoDB + ChromaDB
- **AI**: Gemini 3 Flash via emergentintegrations library (Emergent LLM Key)
- **RAG**: ChromaDB vector database with pix2code + curated templates
- **Dataset**: pix2code public dataset (30 samples) + 16 curated modern UI templates = 46 total

## User Personas
- Students/Researchers wanting to convert UI sketches to code
- Developers prototyping ideas quickly
- Project Proto team members (Ashirwad Singh, Samarth Gupta)

## Core Requirements
- [x] PDF document analysis (Project Proto synopsis)
- [x] Image upload (JPEG/PNG/WEBP)
- [x] Text description input
- [x] Framework selection (React/Vue/Angular/HTML)
- [x] RAG training pipeline with pix2code dataset
- [x] AI-powered code generation (Gemini 3 Flash)
- [x] Code display + copy + download
- [x] Project history
- [x] Project Proto documentation

## What's Been Implemented (Feb 2026)
- Full RAG training pipeline with ChromaDB vector DB
- pix2code dataset integration (30 web DSL samples)
- 16 curated modern React UI templates (login, dashboard, landing, pricing, etc.)
- 4-tab interface: Train → Generate → Code → Docs
- Image analysis + RAG context retrieval + code generation workflow
- Project history stored in MongoDB
- Training status dashboard with pipeline visualization

## Prioritized Backlog
### P0 (Done)
- RAG training pipeline ✅
- Image upload + code generation ✅
- pix2code dataset integration ✅

### P1 (Next)
- Add more datasets (Rico, WebSight, VISION2UI)
- Image-based embeddings using CLIP model
- Code preview/sandbox (live rendering)

### P2 (Future)
- User authentication
- Custom dataset upload
- Fine-tuning support
- Multi-page generation
- Export to project scaffolding
