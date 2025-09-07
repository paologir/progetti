#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from pathlib import Path
import aiofiles
import asyncio
from datetime import datetime

from config import settings
from utils.logger import StructuredLogger
from utils.security import SecurityValidator, RateLimiter, generate_session_id
from chatbot_v2 import RAGChatbot
from ingest_v2 import IngestPipeline


logger = StructuredLogger(__name__, log_file=Path("logs/api.log"))

# FastAPI app
app = FastAPI(
    title="Mistral RAG API",
    description="API REST per il sistema RAG basato su Mistral",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specificare origini consentite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inizializza componenti
chatbot = RAGChatbot()
security_validator = SecurityValidator()
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)


# Modelli Pydantic
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    include_sources: bool = True
    max_chunks: Optional[int] = Field(None, ge=1, le=10)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[str]] = None
    metadata: Dict[str, Any] = {}


class IngestRequest(BaseModel):
    directory: Optional[str] = None


class IngestResponse(BaseModel):
    status: str
    message: str
    stats: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


# Dependency per rate limiting
async def check_rate_limit(session_id: Optional[str] = None):
    if not session_id:
        session_id = "anonymous"
    
    if not rate_limiter.is_allowed(session_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return session_id


# Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Mistral RAG API v2.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    components = {}
    
    # Check vector store
    try:
        chatbot.vector_store.similarity_search("test", k=1)
        components["vector_store"] = "healthy"
    except:
        components["vector_store"] = "unhealthy"
    
    # Check LLM
    try:
        await asyncio.to_thread(chatbot.llm.invoke, "test")
        components["llm"] = "healthy"
    except:
        components["llm"] = "unhealthy"
    
    overall_status = "healthy" if all(v == "healthy" for v in components.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        components=components
    )


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_rate_limit)])
async def chat(request: ChatRequest, session_id: str = Depends(check_rate_limit)):
    """Endpoint principale per il chatbot"""
    try:
        # Usa session_id dalla request se fornito
        if request.session_id:
            session_id = request.session_id
        elif session_id == "anonymous":
            session_id = generate_session_id()
        
        # Genera risposta
        result = await chatbot.generate_response(request.query, session_id)
        
        # Prepara risposta
        response = ChatResponse(
            response=result["response"],
            session_id=session_id,
            sources=result.get("sources") if request.include_sources else None,
            metadata={
                "chunks_used": result.get("chunks_used", 0),
                "response_time": result.get("response_time", 0),
                "cached": result.get("cached", False)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error("Errore in chat endpoint", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, session_id: str = Depends(check_rate_limit)):
    """Endpoint per streaming delle risposte (SSE)"""
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate():
        try:
            # Genera risposta (qui potresti implementare streaming reale)
            result = await chatbot.generate_response(request.query, session_id)
            
            # Simula streaming
            words = result["response"].split()
            for i, word in enumerate(words):
                chunk = {
                    "type": "content",
                    "content": word + " ",
                    "done": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # Simula delay
            
            # Invia metadata finale
            metadata = {
                "type": "metadata",
                "sources": result.get("sources", []),
                "chunks_used": result.get("chunks_used", 0),
                "response_time": result.get("response_time", 0)
            }
            yield f"data: {json.dumps(metadata)}\n\n"
            
        except Exception as e:
            error = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Ottiene la storia di una sessione"""
    history = chatbot.memory.get_history(session_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": history,
        "message_count": len(history)
    }


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Pulisce una sessione"""
    chatbot.memory.clear(session_id)
    return {"message": "Session cleared", "session_id": session_id}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    request: IngestRequest,
    background_tasks: BackgroundTasks
):
    """Avvia processo di ingestione documenti"""
    try:
        directory = Path(request.directory) if request.directory else settings.documents_path
        
        # Valida directory
        if not security_validator.validate_file_path(directory, Path(".")):
            raise HTTPException(status_code=400, detail="Invalid directory path")
        
        if not directory.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        # Avvia ingestione in background
        def run_ingest():
            pipeline = IngestPipeline()
            return pipeline.run(directory)
        
        # Per ora eseguiamo in modo sincrono (in produzione usare Celery o simili)
        result = run_ingest()
        
        return IngestResponse(
            status=result["status"],
            message=result.get("message", "Ingestione completata"),
            stats=result if result["status"] == "success" else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Errore in ingest endpoint", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    process: bool = True
):
    """Upload e processa un singolo documento"""
    try:
        # Valida file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_file_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {settings.allowed_file_extensions}"
            )
        
        # Salva file
        safe_filename = security_validator.sanitize_filename(file.filename)
        file_path = settings.documents_path / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Verifica dimensione
        if not security_validator.validate_file_size(file_path, settings.max_file_size_mb):
            file_path.unlink()  # Rimuovi file
            raise HTTPException(status_code=413, detail="File too large")
        
        response = {
            "filename": safe_filename,
            "size_mb": file_path.stat().st_size / (1024 * 1024),
            "processed": False
        }
        
        # Processa se richiesto
        if process:
            pipeline = IngestPipeline()
            result = pipeline.update_document(file_path)
            response["processed"] = result["status"] == "success"
            response["chunks_added"] = result.get("chunks_added", 0)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Errore in upload endpoint", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Ottiene statistiche del sistema"""
    cache_stats = chatbot.cache.get_stats()
    
    return {
        "cache": cache_stats,
        "sessions": {
            "active": len(chatbot.memory.conversations),
            "total_messages": sum(
                len(conv) for conv in chatbot.memory.conversations.values()
            )
        },
        "rate_limits": {
            "window_seconds": rate_limiter.window_seconds,
            "max_requests": rate_limiter.max_requests
        }
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error("Unhandled exception", exception=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def main():
    """Avvia server"""
    logger.info("Avvio API server...")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # In produzione impostare a False
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )


if __name__ == "__main__":
    main()