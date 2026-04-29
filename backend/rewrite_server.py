import re

with open('server.py', 'r') as f:
    content = f.read()

# remove emergentintegrations
content = re.sub(r'from emergentintegrations.*?LlmChat, UserMessage, ImageContent\n', '', content)

# add imports
content = content.replace('from datetime import datetime, timezone', 'from datetime import datetime, timezone\nfrom fastapi.responses import StreamingResponse\nimport json\nimport base64\nfrom google import genai\nfrom google.genai import types')

new_generate_code = '''
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
            yield f"data: {json.dumps({'status': 'analyzing', 'message': 'Analyzing UI design...'})}\\n\\n"

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
            yield f"data: {json.dumps({'status': 'rag', 'message': 'Retrieving reference examples...'})}\\n\\n"
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
                    rag_context_str = "\\n\\n--- REFERENCE EXAMPLES FROM TRAINING DATA ---\\n"
                    for i, result in enumerate(rag_results):
                        rag_context_str += f"\\n### Example {i+1} (Category: {result['category']}, Similarity: {result['similarity']}):\\n"
                        rag_context_str += f"Description: {result['description']}\\n"
                        rag_context_str += f"Code:\\n```\\n{result['code'][:1500]}\\n```\\n"
                    
                    logging.info(f"RAG retrieved {len(rag_results)} similar examples")
            
            # Step 3: Generate code with RAG context
            yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating code with RAG context...', 'rag_context': rag_results})}\\n\\n"
            
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
                yield f"data: {json.dumps({'status': 'chunk', 'text': chunk.text})}\\n\\n"
            
            # Step 4: Store in MongoDB
            yield f"data: {json.dumps({'status': 'saving', 'message': 'Saving project...'})}\\n\\n"
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
            yield f"data: {json.dumps({'status': 'done', 'project': final_response})}\\n\\n"
            
        except Exception as e:
            logging.error(f"Error generating code: {str(e)}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\\n\\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
'''

content = re.sub(r'@api_router\.post\("/generate", response_model=GeneratedCodeResponse\)\s*async def generate_code.*?except Exception as e:.*?raise HTTPException\(status_code=500, detail=f"Failed to generate code: \{str\(e\)\}"\)', new_generate_code, content, flags=re.DOTALL)

with open('server.py', 'w') as f:
    f.write(content)
