"""
Dedicated Embedding Service Server

A FastAPI-based microservice for generating embeddings with nomic-embed-text.
Supports both text and image embeddings, designed to run on a dedicated PC.

Installation:
    pip install fastapi uvicorn sentence-transformers pillow torch

Usage:
    # CPU only
    python embedding_server.py
    
    # With GPU
    CUDA_VISIBLE_DEVICES=0 python embedding_server.py
    
    # Custom host/port
    python embedding_server.py --host 0.0.0.0 --port 8000
    
    # Production (multiple workers)
    uvicorn embedding_server:app --host 0.0.0.0 --port 8000 --workers 4
"""

import argparse
import base64
import io
import time
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import torch
from sentence_transformers import SentenceTransformer
from PIL import Image


# Model cache
_model_cache: Dict[str, SentenceTransformer] = {}


def get_model(model_name: str = "nomic-embed-text") -> SentenceTransformer:
    """Get or load an embedding model."""
    if model_name not in _model_cache:
        print(f"Loading model: {model_name}")
        
        # Map friendly names to actual model paths
        model_map = {
            "nomic-embed-text": "nomic-ai/nomic-embed-text-v1.5",
            "nomic-embed-text-v1": "nomic-ai/nomic-embed-text-v1",
            "nomic-embed-text-v1.5": "nomic-ai/nomic-embed-text-v1.5",
        }
        
        actual_model = model_map.get(model_name, model_name)
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model = SentenceTransformer(actual_model, device=device)
        _model_cache[model_name] = model
        print(f"Model {model_name} loaded successfully")
    
    return _model_cache[model_name]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Preload default model
    print("=== Embedding Service Starting ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Preload default model
    get_model("nomic-embed-text")
    print("=== Embedding Service Ready ===")
    
    yield
    
    # Shutdown
    print("=== Embedding Service Shutting Down ===")


app = FastAPI(
    title="Nico Embedding Service",
    description="Dedicated embedding service for text and image vectors",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TextEmbedRequest(BaseModel):
    """Request for text embeddings."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: str = Field("nomic-embed-text", description="Embedding model to use")
    normalize: bool = Field(True, description="Whether to normalize embeddings")


class ImageEmbedRequest(BaseModel):
    """Request for image embeddings."""
    images: List[str] = Field(..., description="List of base64-encoded images")
    model: str = Field("nomic-embed-text", description="Embedding model to use")
    normalize: bool = Field(True, description="Whether to normalize embeddings")


class EmbedResponse(BaseModel):
    """Response containing embeddings."""
    embeddings: List[List[float]]
    model: str
    dimension: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    models_loaded: List[str]
    device: str
    cuda_available: bool


# Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "service": "Nico Embedding Service",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        models_loaded=list(_model_cache.keys()),
        device="cuda" if torch.cuda.is_available() else "cpu",
        cuda_available=torch.cuda.is_available()
    )


@app.post("/embed/text", response_model=EmbedResponse)
async def embed_text(request: TextEmbedRequest):
    """
    Generate embeddings for text.
    
    Example:
        ```
        POST /embed/text
        {
            "texts": ["Hello world", "Another text"],
            "model": "nomic-embed-text"
        }
        ```
    """
    if not request.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    try:
        start_time = time.time()
        
        model = get_model(request.model)
        
        # Generate embeddings
        embeddings = model.encode(
            request.texts,
            convert_to_numpy=True,
            normalize_embeddings=request.normalize,
            show_progress_bar=False
        )
        
        # Convert to list
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmbedResponse(
            embeddings=embeddings_list,
            model=request.model,
            dimension=len(embeddings_list[0]),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")


@app.post("/embed/image", response_model=EmbedResponse)
async def embed_image(request: ImageEmbedRequest):
    """
    Generate embeddings for images.
    
    Example:
        ```
        POST /embed/image
        {
            "images": ["base64_encoded_image_data..."],
            "model": "nomic-embed-text"
        }
        ```
    """
    if not request.images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    try:
        start_time = time.time()
        
        model = get_model(request.model)
        
        # Decode base64 images
        pil_images = []
        for img_b64 in request.images:
            img_bytes = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_bytes))
            pil_images.append(img)
        
        # Generate embeddings
        embeddings = model.encode(
            pil_images,
            convert_to_numpy=True,
            normalize_embeddings=request.normalize,
            show_progress_bar=False
        )
        
        # Convert to list
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        processing_time = (time.time() - start_time) * 1000
        
        return EmbedResponse(
            embeddings=embeddings_list,
            model=request.model,
            dimension=len(embeddings_list[0]),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image embedding failed: {str(e)}")


@app.get("/models", response_model=Dict[str, Any])
async def list_models():
    """List available models."""
    return {
        "available_models": [
            "nomic-embed-text",
            "nomic-embed-text-v1",
            "nomic-embed-text-v1.5"
        ],
        "loaded_models": list(_model_cache.keys())
    }


@app.post("/warmup")
async def warmup(model: str = "nomic-embed-text"):
    """Warmup a model by loading it into memory."""
    try:
        get_model(model)
        return {"status": "success", "model": model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Warmup failed: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nico Embedding Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    import uvicorn
    
    print(f"\n🚀 Starting Embedding Service on {args.host}:{args.port}")
    print(f"📝 API docs: http://{args.host}:{args.port}/docs")
    print(f"🔧 Health check: http://{args.host}:{args.port}/health\n")
    
    uvicorn.run(
        "embedding_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
