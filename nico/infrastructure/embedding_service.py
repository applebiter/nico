"""Embedding service client for distributed vector encoding."""
import asyncio
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import base64
import aiohttp


class EmbeddingServiceClient:
    """Client for communicating with a dedicated embedding service."""
    
    def __init__(self, endpoint: str = "http://localhost:8000"):
        """
        Initialize the embedding service client.
        
        Args:
            endpoint: Base URL of the embedding service (e.g., "http://192.168.1.50:8000")
        """
        self.endpoint = endpoint.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_health(self) -> bool:
        """
        Check if the embedding service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.endpoint}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"Embedding service health check failed: {e}")
            return False
    
    async def embed_text(
        self, 
        text: Union[str, List[str]], 
        model: str = "nomic-embed-text"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text string or list of texts
            model: Embedding model to use (default: nomic-embed-text)
        
        Returns:
            Single embedding vector or list of embedding vectors
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.post(
            f"{self.endpoint}/embed/text",
            json={
                "texts": texts,
                "model": model
            },
            timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            embeddings = data["embeddings"]
            return embeddings[0] if is_single else embeddings
    
    async def embed_image(
        self,
        image_path: Union[str, Path, List[Union[str, Path]]],
        model: str = "nomic-embed-text"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for images.
        
        Args:
            image_path: Single image path or list of image paths
            model: Embedding model to use (default: nomic-embed-text)
        
        Returns:
            Single embedding vector or list of embedding vectors
        """
        is_single = isinstance(image_path, (str, Path))
        paths = [Path(image_path)] if is_single else [Path(p) for p in image_path]
        
        # Encode images to base64
        images_b64 = []
        for path in paths:
            with open(path, 'rb') as f:
                img_bytes = f.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                images_b64.append(img_b64)
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.post(
            f"{self.endpoint}/embed/image",
            json={
                "images": images_b64,
                "model": model
            },
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            embeddings = data["embeddings"]
            return embeddings[0] if is_single else embeddings
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        model: str = "nomic-embed-text"
    ) -> List[List[float]]:
        """
        Generate embeddings for a large batch of texts with automatic batching.
        
        Args:
            texts: List of text strings
            batch_size: Number of texts per batch
            model: Embedding model to use
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self.embed_text(batch, model=model)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors (if service provides search capability).
        
        Args:
            query_embedding: Query vector
            limit: Number of results to return
            filters: Optional filters for the search
        
        Returns:
            List of similar results with scores
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.post(
            f"{self.endpoint}/search",
            json={
                "embedding": query_embedding,
                "limit": limit,
                "filters": filters or {}
            },
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["results"]


class LocalEmbeddingFallback:
    """Fallback to local embeddings if service is unavailable."""
    
    def __init__(self):
        self._model = None
    
    def _ensure_model(self):
        """Lazy load the local embedding model."""
        if self._model is None:
            try:
                # Try to import sentence-transformers for local fallback
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5')
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Generate embeddings locally."""
        self._ensure_model()
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        return embeddings_list[0] if is_single else embeddings_list


class EmbeddingManager:
    """
    Manager that tries remote service first, falls back to local.
    """
    
    def __init__(self, service_endpoint: Optional[str] = None, use_fallback: bool = True):
        """
        Initialize the embedding manager.
        
        Args:
            service_endpoint: Remote embedding service URL (None to use local only)
            use_fallback: Whether to fall back to local embeddings if service fails
        """
        self.service_endpoint = service_endpoint
        self.use_fallback = use_fallback
        self.client: Optional[EmbeddingServiceClient] = None
        self.fallback: Optional[LocalEmbeddingFallback] = None
        self._service_available: Optional[bool] = None
    
    async def initialize(self):
        """Initialize the manager and check service availability."""
        if self.service_endpoint:
            self.client = EmbeddingServiceClient(self.service_endpoint)
            self._service_available = await self.client.check_health()
            
            if not self._service_available:
                print(f"Warning: Embedding service at {self.service_endpoint} is not available")
                if self.use_fallback:
                    print("Will use local embeddings as fallback")
        
        if self.use_fallback and (not self.service_endpoint or not self._service_available):
            self.fallback = LocalEmbeddingFallback()
    
    async def embed_text(
        self, 
        text: Union[str, List[str]], 
        model: str = "nomic-embed-text"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate text embeddings, trying service first then fallback.
        
        Args:
            text: Single text or list of texts
            model: Model to use
        
        Returns:
            Embedding vector(s)
        """
        # Try service first
        if self.client and self._service_available:
            try:
                return await self.client.embed_text(text, model)
            except Exception as e:
                print(f"Embedding service failed: {e}")
                if not self.use_fallback:
                    raise
        
        # Fall back to local
        if self.fallback:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.fallback.embed_text, text)
        
        raise RuntimeError("No embedding method available (service down and no fallback)")
    
    async def embed_image(
        self,
        image_path: Union[str, Path, List[Union[str, Path]]],
        model: str = "nomic-embed-text"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate image embeddings (requires service, no local fallback).
        
        Args:
            image_path: Single path or list of paths
            model: Model to use
        
        Returns:
            Embedding vector(s)
        """
        if not self.client or not self._service_available:
            raise RuntimeError(
                "Image embeddings require the embedding service. "
                "No local fallback available."
            )
        
        return await self.client.embed_image(image_path, model)


# Global instance
_embedding_manager: Optional[EmbeddingManager] = None


async def get_embedding_manager(
    service_endpoint: Optional[str] = None,
    use_fallback: bool = True
) -> EmbeddingManager:
    """
    Get the global embedding manager instance.
    
    Args:
        service_endpoint: Remote service URL (e.g., "http://192.168.1.50:8000")
        use_fallback: Whether to use local fallback
    
    Returns:
        Initialized embedding manager
    """
    global _embedding_manager
    
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager(service_endpoint, use_fallback)
        await _embedding_manager.initialize()
    
    return _embedding_manager
