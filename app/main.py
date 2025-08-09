# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from .langflow_runner import LangFlowRunner

# Load environment variables FIRST
load_dotenv()

app = FastAPI(
    title="AI Customer Support API",
    description="Multi-agent customer support system with auto-routing",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize LangFlow runner
langflow = LangFlowRunner()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    conversation_id: str
    confidence: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with multi-agent routing"""
    
    try:
        result = await langflow.run_flow(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            response=result.get("response", "I apologise, but I couldn't process your request."),
            agent_type=result.get("agent_type", "general"),
            conversation_id=result.get("conversation_id", request.conversation_id or "new"),
            confidence=result.get("confidence", "medium")
        )
    
    except Exception as e:
        print(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Customer Support API"}

@app.get("/api/agents")
async def get_agents():
    """Get available agent types"""
    return {
        "agents": [
            {"id": "general", "name": "General Support", "description": "Returns, shipping, policies"},
            {"id": "product", "name": "Product Specialist", "description": "Product specs, pricing, features"},
            {"id": "technical", "name": "Technical Support", "description": "Troubleshooting, setup, repairs"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)