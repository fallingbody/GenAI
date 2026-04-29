from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import threading
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
import json
import base64
from google import genai
from google.genai import types
from rag_service import rag_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# --- Models ---

class GenerateCodeRequest(BaseModel):
    image_base64: str
    project_name: str
    description: str
    framework: Optional[str] = "React"

class GeneratedCodeResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    project_name: str
    description: str
    framework: str
    generated_code: str
    rag_context: Optional[List[Dict]] = []
    timestamp: datetime

class ProjectHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    project_name: str
    description: str
    framework: str
    timestamp: datetime

class TrainingStatus(BaseModel):
    is_trained: bool
    total_entries: int
    stats: Dict
    storage_path: str

class RAGQueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5
    framework: Optional[str] = None

# --- Routes ---

@api_router.get("/")
async def root():
    return {"message": "Proto - AI Frontend Generator API with RAG Training Pipeline"}

# Training state
training_state = {"is_training": False, "progress": "", "error": None}

def run_training():
    """Run training in background thread."""
    global training_state
    training_state = {"is_training": True, "progress": "Downloading pix2code dataset from HuggingFace...", "error": None}
    try:
        stats = rag_service.train()
        training_state = {"is_training": False, "progress": "Complete", "error": None, "stats": stats}
    except Exception as e:
        training_state = {"is_training": False, "progress": "Failed", "error": str(e)}
        logging.error(f"Training error: {str(e)}")

@api_router.post("/train")
async def train_rag():
    """Start RAG training in background."""
    global training_state
    if training_state.get("is_training"):
        return {"status": "already_training", "message": "Training is already in progress", "progress": training_state["progress"]}
    
    thread = threading.Thread(target=run_training, daemon=True)
    thread.start()
    
    return {"status": "started", "message": "Training started in background. Poll /api/training-status for progress."}

@api_router.get("/training-status")
async def get_training_status():
    """Get current training status."""
    status = rag_service.get_status()
    status["is_training"] = training_state.get("is_training", False)
    status["training_progress"] = training_state.get("progress", "")
    status["training_error"] = training_state.get("error")
    if "stats" in training_state and training_state["stats"]:
        status["stats"] = training_state["stats"]
    return status

@api_router.post("/rag-query")
async def rag_query(request: RAGQueryRequest):
    """Query the RAG system directly."""
    status = rag_service.get_status()
    if not status["is_trained"] and status["total_entries"] == 0:
        raise HTTPException(status_code=400, detail="RAG system not trained yet. Call /api/train first.")
    
    results = rag_service.query(request.query, request.n_results, request.framework)
    return {"results": results, "query": request.query}


@api_router.post("/generate")
async def generate_code(request: GenerateCodeRequest):
    """Generate code using RAG-enhanced AI pipeline and stream the result."""
    api_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    genai_client = genai.Client(api_key=api_key)

    async def event_generator():
        try:
            # Step 1: Analyze image with Gemini
            session_id = str(uuid.uuid4())
            yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Analyzing UI design...'})}\n\n"

            image_bytes = base64.b64decode(request.image_base64)
            image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')

            analysis_prompt = "You are a UI analysis expert. Describe the UI elements, layout structure, and design patterns you see in the image. Be specific about component types (forms, cards, navigation, etc), layout (grid, flex, columns), and visual hierarchy. Analyze this UI design/sketch. Describe the layout, components, and structure in detail."
            
            analysis_response = await genai_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=[analysis_prompt, image_part]
            )
            image_analysis = analysis_response.text
            logging.info(f"Image analysis complete: {image_analysis[:200]}...")

            # Step 2: Query RAG for similar UI examples
            yield f"data: {json.dumps({'status': 'rag', 'message': 'Retrieving reference examples...'})}\n\n"
            rag_results = []
            rag_context_str = ""
            status = rag_service.get_status()
            
            if status["total_entries"] > 0:
                combined_query = f"{request.description}. {image_analysis[:500]}"
                rag_results = rag_service.query(
                    combined_query, 
                    n_results=3,
                    framework=request.framework
                )
                
                if rag_results:
                    rag_context_str = "\n\n--- REFERENCE EXAMPLES FROM TRAINING DATA ---\n"
                    for i, result in enumerate(rag_results):
                        rag_context_str += f"\n### Example {i+1} (Category: {result['category']}, Similarity: {result['similarity']}):\n"
                        rag_context_str += f"Description: {result['description']}\n"
                        rag_context_str += f"Code:\n```\n{result['code'][:1500]}\n```\n"
                    
                    logging.info(f"RAG retrieved {len(rag_results)} similar examples")
            
            # Step 3: Generate code with RAG context
            yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating code with RAG context...', 'rag_context': rag_results})}\n\n"
            
            generation_prompt = f"""You are an expert frontend developer. Generate complete, production-ready frontend code.
Use the reference examples from the training dataset as inspiration for structure and patterns.
Adapt them to match the specific requirements and the uploaded design.
Based on this UI analysis and user requirements, generate complete frontend code.

## Image Analysis:
{image_analysis}

## User Requirements:
- Project: {request.project_name}
- Framework: {request.framework}
- Description: {request.description}

{rag_context_str}

## Instructions:
1. Use the reference examples above as structural patterns to follow
2. Adapt the design to match the uploaded UI sketch
3. Generate clean, production-ready {request.framework} code
4. Include all necessary imports and components
5. Use Tailwind CSS for styling
6. Make it responsive

Return ONLY the complete code, no explanations."""

            response_stream = await genai_client.aio.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=[generation_prompt, image_part]
            )
            
            generated_code = ""
            async for chunk in response_stream:
                generated_code += chunk.text
                yield f"data: {json.dumps({'status': 'chunk', 'text': chunk.text})}\n\n"
            
            # Step 4: Store in MongoDB
            yield f"data: {json.dumps({'status': 'saving', 'message': 'Saving project...'})}\n\n"
            project_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)
            
            rag_context_for_db = [
                {"id": r["id"], "category": r["category"], "similarity": r["similarity"]}
                for r in rag_results
            ]
            
            doc = {
                "id": project_id,
                "project_name": request.project_name,
                "description": request.description,
                "framework": request.framework,
                "generated_code": generated_code,
                "image_analysis": image_analysis,
                "rag_context": rag_context_for_db,
                "timestamp": timestamp.isoformat()
            }
            
            await db.generated_projects.insert_one(doc)
            
            final_response = {
                "id": project_id,
                "project_name": request.project_name,
                "description": request.description,
                "framework": request.framework,
                "generated_code": generated_code,
                "rag_context": rag_context_for_db,
                "timestamp": timestamp.isoformat()
            }
            yield f"data: {json.dumps({'status': 'done', 'project': final_response})}\n\n"
            
        except Exception as e:
            logging.error(f"Error generating code: {str(e)}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@api_router.get("/projects", response_model=List[ProjectHistory])
async def get_projects():
    try:
        projects = await db.generated_projects.find(
            {}, 
            {"_id": 0, "id": 1, "project_name": 1, "description": 1, "framework": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(20).to_list(20)
        
        for project in projects:
            if isinstance(project['timestamp'], str):
                project['timestamp'] = datetime.fromisoformat(project['timestamp'])
        
        return projects
    except Exception as e:
        logging.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    try:
        project = await db.generated_projects.find_one({"id": project_id}, {"_id": 0})
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if isinstance(project['timestamp'], str):
            project['timestamp'] = datetime.fromisoformat(project['timestamp'])
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/dataset-info")
async def get_dataset_info_endpoint():
    """Get information about the public pix2code dataset."""
    from dataset_generator import get_dataset_info
    return get_dataset_info()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
