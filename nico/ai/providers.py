"""LLM provider implementations for different services."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import json


class ProviderType(Enum):
    """Types of LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"


@dataclass
class LLMConfig:
    """Configuration for an LLM instance."""
    id: str  # Unique identifier
    name: str  # Display name
    provider: ProviderType
    model: str
    endpoint: Optional[str] = None  # For Ollama or custom endpoints
    api_key: Optional[str] = None  # For API-based providers
    temperature: float = 0.7
    max_tokens: int = 2000
    enabled: bool = True
    # Capabilities
    supports_streaming: bool = True
    supports_function_calling: bool = True
    # Performance hints
    speed_tier: str = "medium"  # fast, medium, slow
    cost_tier: str = "low"  # free, low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d['provider'] = self.provider.value
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """Create from dictionary."""
        data['provider'] = ProviderType(data['provider'])
        return cls(**data)


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._is_available: Optional[bool] = None
        self._warmed_up: bool = False
    
    @abstractmethod
    async def check_availability(self) -> bool:
        """Check if the provider/model is available."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response."""
        pass
    
    async def warm_up(self) -> bool:
        """Warm up the model with a simple prompt."""
        try:
            await self.generate("Hello", max_tokens=5)
            self._warmed_up = True
            return True
        except Exception as e:
            print(f"Warmup failed for {self.config.name}: {e}")
            return False
    
    @property
    def is_warmed_up(self) -> bool:
        """Check if model is warmed up."""
        return self._warmed_up
    
    @property
    async def is_available(self) -> bool:
        """Check if provider is available (cached)."""
        if self._is_available is None:
            self._is_available = await self.check_availability()
        return self._is_available


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # Default to localhost if no endpoint specified
        if not config.endpoint:
            config.endpoint = "http://localhost:11434"
    
    async def check_availability(self) -> bool:
        """Check if Ollama endpoint is available and model exists."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Check if endpoint is responding
                async with session.get(f"{self.config.endpoint}/api/tags", timeout=5) as resp:
                    if resp.status != 200:
                        return False
                    
                    # Check if model is available
                    data = await resp.json()
                    models = [m['name'] for m in data.get('models', [])]
                    return self.config.model in models
        except Exception as e:
            print(f"Ollama availability check failed: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Ollama."""
        import aiohttp
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.endpoint}/api/generate",
                json=payload,
                timeout=60
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Ollama error: {resp.status}")
                
                result = await resp.json()
                return result.get("response", "")
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using Ollama."""
        import aiohttp
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.endpoint}/api/generate",
                json=payload,
                timeout=120
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Ollama error: {resp.status}")
                
                async for line in resp.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if chunk := data.get("response"):
                                yield chunk
                        except json.JSONDecodeError:
                            continue


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    async def check_availability(self) -> bool:
        """Check if OpenAI API key is valid."""
        if not self.config.api_key:
            return False
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=5
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using OpenAI."""
        import aiohttp
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"OpenAI error: {error}")
                
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using OpenAI."""
        import aiohttp
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"OpenAI error: {error}")
                
                async for line in resp.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if delta := data["choices"][0]["delta"].get("content"):
                                    yield delta
                            except json.JSONDecodeError:
                                continue


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    async def check_availability(self) -> bool:
        """Check if Anthropic API key is valid."""
        if not self.config.api_key:
            return False
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Simple check - try to make a minimal request
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.config.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.config.model,
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "Hi"}]
                    },
                    timeout=5
                ) as resp:
                    return resp.status in (200, 400)  # 400 is ok, means auth worked
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Anthropic."""
        import aiohttp
        
        payload = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload,
                timeout=60
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Anthropic error: {error}")
                
                result = await resp.json()
                return result["content"][0]["text"]
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using Anthropic."""
        import aiohttp
        
        payload = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True,
        }
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload,
                timeout=120
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Anthropic error: {error}")
                
                async for line in resp.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    if text := data.get("delta", {}).get("text"):
                                        yield text
                            except json.JSONDecodeError:
                                continue


class GoogleProvider(BaseLLMProvider):
    """Google Gemini API provider."""
    
    async def check_availability(self) -> bool:
        """Check if Google API key is valid."""
        if not self.config.api_key:
            return False
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={self.config.api_key}",
                    timeout=5
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Google Gemini."""
        import aiohttp
        
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": system}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1/models/{self.config.model}:generateContent?key={self.config.api_key}",
                json=payload,
                timeout=60
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Google error: {error}")
                
                result = await resp.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using Google Gemini."""
        import aiohttp
        
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": system}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1/models/{self.config.model}:streamGenerateContent?key={self.config.api_key}",
                json=payload,
                timeout=120
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Google error: {error}")
                
                async for line in resp.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if candidates := data.get("candidates"):
                                if text := candidates[0].get("content", {}).get("parts", [{}])[0].get("text"):
                                    yield text
                        except json.JSONDecodeError:
                            continue


class GrokProvider(BaseLLMProvider):
    """xAI Grok API provider."""
    
    async def check_availability(self) -> bool:
        """Check if Grok API key is valid."""
        if not self.config.api_key:
            return False
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.x.ai/v1/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=5
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using Grok (OpenAI-compatible API)."""
        import aiohttp
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Grok error: {error}")
                
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
    
    async def stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using Grok."""
        import aiohttp
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Grok error: {error}")
                
                async for line in resp.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if delta := data["choices"][0]["delta"].get("content"):
                                    yield delta
                            except json.JSONDecodeError:
                                continue


def create_provider(config: LLMConfig) -> BaseLLMProvider:
    """Factory function to create appropriate provider."""
    providers = {
        ProviderType.OLLAMA: OllamaProvider,
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.ANTHROPIC: AnthropicProvider,
        ProviderType.GOOGLE: GoogleProvider,
        ProviderType.GROK: GrokProvider,
    }
    
    provider_class = providers.get(config.provider)
    if not provider_class:
        raise ValueError(f"Unknown provider type: {config.provider}")
    
    return provider_class(config)
