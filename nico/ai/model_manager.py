"""Ollama model manager for hot-swapping between text and vision models."""
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import base64
from pathlib import Path


class ModelType(Enum):
    """Types of models available."""
    TEXT = "text"  # General text generation
    VISION = "vision"  # Vision-language model


@dataclass
class ModelStatus:
    """Status of a model."""
    name: str
    loaded: bool
    in_vram: bool
    size_gb: float
    last_used: Optional[float] = None


class OllamaModelManager:
    """Manages Ollama models with hot-swapping between VRAM and RAM."""
    
    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
        self.text_model = "granite4:3b"  # Tool-using, non-thinking model
        self.vision_model = "ministral-3:3b"  # Tool-using vision model
        self.current_model: Optional[str] = None
        self._model_cache: Dict[str, ModelStatus] = {}
    
    async def check_ollama_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/api/tags", timeout=3) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def list_models(self) -> list[str]:
        """List all available models."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.endpoint}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
        return []
    
    async def load_model(self, model_name: str, keep_alive: str = "5m") -> bool:
        """Load a model into memory.
        
        Args:
            model_name: Name of the model to load
            keep_alive: How long to keep in VRAM (e.g., "5m", "1h", "-1" for indefinite)
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Simple generate call loads the model
                payload = {
                    "model": model_name,
                    "prompt": "Hello",
                    "stream": False,
                    "keep_alive": keep_alive,
                    "options": {"num_predict": 1}
                }
                async with session.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=30
                ) as resp:
                    if resp.status == 200:
                        self.current_model = model_name
                        return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
        return False
    
    async def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_name,
                    "keep_alive": 0  # Unload immediately
                }
                async with session.post(
                    f"{self.endpoint}/api/generate",
                    json=payload
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Error unloading model {model_name}: {e}")
        return False
    
    async def generate_text(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        tools: Optional[list[Dict[str, Any]]] = None
    ) -> str:
        """Generate text using the text model."""
        # Switch to text model if needed
        if self.current_model != self.text_model:
            await self.switch_to_text()
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.text_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 4096,  # Context window
                    # Disable thinking for faster responses
                    "top_k": 40,
                    "top_p": 0.9,
                }
            }
            
            if system:
                payload["system"] = system
            
            if tools:
                payload["tools"] = tools
            
            async with session.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    # Handle different response formats
                    response_text = result.get("response", "").strip()
                    if not response_text and "message" in result:
                        response_text = result["message"].get("content", "")
                    return response_text
                else:
                    text = await resp.text()
                    raise Exception(f"Generate failed ({resp.status}): {text}")
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str = "Describe this image in detail.",
        temperature: float = 0.3
    ) -> str:
        """Analyze an image using the vision model.
        
        Args:
            image_path: Path to the image file
            prompt: Question or instruction about the image
            temperature: Lower for more consistent descriptions
        """
        # Switch to vision model if needed
        if self.current_model != self.vision_model:
            await self.switch_to_vision()
        
        # Read and encode image
        image_data = Path(image_path).read_bytes()
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 200,
                    "num_ctx": 4096,
                }
            }
            
            async with session.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    response_text = result.get("response", "")
                    if not response_text and "message" in result:
                        response_text = result["message"].get("content", "")
                    return response_text.strip()
                else:
                    text = await resp.text()
                    raise Exception(f"Vision analysis failed ({resp.status}): {text}")
    
    async def approve_image(
        self,
        image_path: str,
        context: str,
        criteria: Optional[str] = None
    ) -> tuple[bool, str]:
        """Use vision model to approve/reject a generated image.
        
        Args:
            image_path: Path to the generated image
            context: Story context (e.g., "A knight in shining armor")
            criteria: Optional specific criteria for approval
        
        Returns:
            (approved: bool, reason: str)
        """
        prompt = f"""You are reviewing an AI-generated image for a story.

Context: {context}

{f"Criteria: {criteria}" if criteria else ""}

Analyze this image and respond ONLY with a JSON object:
{{
    "approved": true/false,
    "reason": "brief explanation",
    "quality_score": 0-10,
    "issues": ["list", "of", "issues"]
}}"""
        
        response = await self.analyze_image(image_path, prompt, temperature=0.1)
        
        # Parse JSON response
        try:
            import json
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            return result.get("approved", False), result.get("reason", "Unknown")
        except Exception as e:
            print(f"Error parsing approval response: {e}")
            # Fallback to simple text analysis
            return "approved" in response.lower() or "accept" in response.lower(), response
    
    async def switch_to_text(self) -> bool:
        """Switch to text model (unload vision, load text)."""
        if self.current_model == self.text_model:
            return True
        
        # Unload vision model if loaded
        if self.current_model == self.vision_model:
            await self.unload_model(self.vision_model)
        
        # Load text model with 10 minute keep-alive
        return await self.load_model(self.text_model, keep_alive="10m")
    
    async def switch_to_vision(self) -> bool:
        """Switch to vision model (unload text, load vision)."""
        if self.current_model == self.vision_model:
            return True
        
        # Unload text model if loaded
        if self.current_model == self.text_model:
            await self.unload_model(self.text_model)
        
        # Load vision model with shorter keep-alive (vision less frequent)
        return await self.load_model(self.vision_model, keep_alive="5m")
    
    async def suggest_autocomplete(
        self,
        field_type: str,
        current_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Generate autocomplete suggestion for an input field.
        
        Args:
            field_type: Type of field (e.g., "character_name", "description", "dialogue")
            current_text: Current text in the field
            context: Additional context (character info, story genre, etc.)
        """
        if len(current_text) < 3:
            return None
        
        prompts = {
            "character_name": f"Complete this character name with 1-2 words: {current_text}",
            "description": f"Continue this description naturally with 5-15 words: {current_text}",
            "dialogue": f"Complete this dialogue naturally: {current_text}",
            "location": f"Complete this location name: {current_text}",
            "occupation": f"Complete this occupation: {current_text}",
        }
        
        prompt = prompts.get(field_type, f"Complete this text naturally: {current_text}")
        
        # Add context if available
        if context:
            prompt = f"Context: {context.get('genre', 'Fiction')}\n\n{prompt}"
        
        try:
            result = await self.generate_text(
                prompt,
                system="You are a creative writing assistant. Complete the text naturally and concisely. Return ONLY the completion, no explanations.",
                temperature=0.7,
                max_tokens=30
            )
            
            # Clean up the result
            result = result.strip()
            # Remove the original text if model repeated it
            if result.startswith(current_text):
                result = result[len(current_text):].strip()
            
            return result if result else None
        except Exception as e:
            print(f"Autocomplete error: {e}")
            return None


# Singleton instance
_model_manager: Optional[OllamaModelManager] = None


def get_model_manager() -> OllamaModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = OllamaModelManager()
    return _model_manager
