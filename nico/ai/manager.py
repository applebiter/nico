"""LLM Team Manager - coordinates multiple LLM instances."""
from typing import List, Dict, Any, Optional
import asyncio
from nico.ai.providers import LLMConfig, BaseLLMProvider, create_provider, ProviderType


class LLMTeam:
    """Manages a team of LLM instances."""
    
    def __init__(self):
        self.members: Dict[str, BaseLLMProvider] = {}
        self.configs: Dict[str, LLMConfig] = {}
        self._primary_id: Optional[str] = None
    
    def add_member(self, config: LLMConfig) -> None:
        """Add an LLM to the team."""
        provider = create_provider(config)
        self.members[config.id] = provider
        self.configs[config.id] = config
        
        # First enabled member becomes primary
        if config.enabled and self._primary_id is None:
            self._primary_id = config.id
    
    def remove_member(self, llm_id: str) -> None:
        """Remove an LLM from the team."""
        if llm_id in self.members:
            del self.members[llm_id]
            del self.configs[llm_id]
            
            # Update primary if removed
            if self._primary_id == llm_id:
                self._primary_id = self._get_next_enabled_id()
    
    def get_member(self, llm_id: str) -> Optional[BaseLLMProvider]:
        """Get a specific team member."""
        return self.members.get(llm_id)
    
    def get_primary(self) -> Optional[BaseLLMProvider]:
        """Get the primary LLM provider."""
        if self._primary_id:
            return self.members.get(self._primary_id)
        return None
    
    def get_primary_config(self) -> Optional[LLMConfig]:
        """Get the primary LLM configuration."""
        if self._primary_id:
            return self.configs.get(self._primary_id)
        return None
    
    def set_primary(self, llm_id: str) -> None:
        """Set a team member as primary."""
        if llm_id in self.members and self.configs[llm_id].enabled:
            self._primary_id = llm_id
    
    def list_members(self, enabled_only: bool = False) -> List[LLMConfig]:
        """List all team members."""
        configs = list(self.configs.values())
        if enabled_only:
            configs = [c for c in configs if c.enabled]
        return configs
    
    def get_by_capability(
        self,
        speed_tier: Optional[str] = None,
        cost_tier: Optional[str] = None,
        supports_function_calling: Optional[bool] = None
    ) -> List[BaseLLMProvider]:
        """Get team members by capability."""
        matches = []
        
        for llm_id, config in self.configs.items():
            if not config.enabled:
                continue
            
            if speed_tier and config.speed_tier != speed_tier:
                continue
            
            if cost_tier and config.cost_tier != cost_tier:
                continue
            
            if supports_function_calling is not None and config.supports_function_calling != supports_function_calling:
                continue
            
            matches.append(self.members[llm_id])
        
        return matches
    
    async def check_all_availability(self) -> Dict[str, bool]:
        """Check availability of all team members."""
        results = {}
        
        tasks = []
        ids = []
        
        for llm_id, provider in self.members.items():
            tasks.append(provider.check_availability())
            ids.append(llm_id)
        
        availability = await asyncio.gather(*tasks, return_exceptions=True)
        
        for llm_id, result in zip(ids, availability):
            if isinstance(result, bool):
                results[llm_id] = result
            else:
                results[llm_id] = False
        
        return results
    
    async def warm_up_all(self, enabled_only: bool = True) -> Dict[str, bool]:
        """Warm up all (or enabled) team members."""
        results = {}
        
        tasks = []
        ids = []
        
        for llm_id, provider in self.members.items():
            if enabled_only and not self.configs[llm_id].enabled:
                continue
            
            tasks.append(provider.warm_up())
            ids.append(llm_id)
        
        warmup_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for llm_id, result in zip(ids, warmup_results):
            if isinstance(result, bool):
                results[llm_id] = result
            else:
                results[llm_id] = False
        
        return results
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system: Optional[str] = None,
        preferred_ids: Optional[List[str]] = None,
        **kwargs
    ) -> tuple[str, str]:
        """
        Generate with automatic fallback to other team members.
        
        Returns:
            Tuple of (response, llm_id_used)
        """
        # Determine order to try
        if preferred_ids:
            try_order = preferred_ids.copy()
        elif self._primary_id:
            try_order = [self._primary_id]
        else:
            try_order = []
        
        # Add other enabled members as fallbacks
        for llm_id, config in self.configs.items():
            if config.enabled and llm_id not in try_order:
                try_order.append(llm_id)
        
        last_error = None
        
        for llm_id in try_order:
            if llm_id not in self.members:
                continue
            
            try:
                provider = self.members[llm_id]
                response = await provider.generate(prompt, system, **kwargs)
                return response, llm_id
            
            except Exception as e:
                last_error = e
                print(f"LLM {llm_id} failed: {e}")
                continue
        
        # All failed
        if last_error:
            raise Exception(f"All LLMs failed. Last error: {last_error}")
        else:
            raise Exception("No enabled LLMs available")
    
    async def parallel_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        llm_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate responses from multiple LLMs in parallel.
        
        Useful for comparing outputs or getting diverse perspectives.
        """
        if llm_ids is None:
            llm_ids = [llm_id for llm_id, config in self.configs.items() if config.enabled]
        
        tasks = []
        ids = []
        
        for llm_id in llm_ids:
            if llm_id not in self.members:
                continue
            
            provider = self.members[llm_id]
            tasks.append(provider.generate(prompt, system, **kwargs))
            ids.append(llm_id)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        responses = {}
        for llm_id, result in zip(ids, results):
            if isinstance(result, str):
                responses[llm_id] = result
            else:
                responses[llm_id] = f"Error: {result}"
        
        return responses
    
    async def route_by_task(
        self,
        prompt: str,
        task_type: str,
        system: Optional[str] = None,
        **kwargs
    ) -> tuple[str, str]:
        """
        Route to appropriate LLM based on task type.
        
        Task types:
        - "quick": Fast, cheap models for simple tasks
        - "creative": Models good at creative writing
        - "analytical": Models good at analysis
        - "coding": Models with function calling for structured output
        """
        if task_type == "quick":
            # Use fastest, cheapest model
            candidates = self.get_by_capability(speed_tier="fast", cost_tier="free")
            if not candidates:
                candidates = self.get_by_capability(cost_tier="low")
        
        elif task_type == "creative":
            # Prefer medium/slow models (usually better quality)
            candidates = self.get_by_capability(speed_tier="medium")
            if not candidates:
                candidates = self.get_by_capability(speed_tier="slow")
        
        elif task_type == "analytical":
            # Use models with good reasoning
            candidates = list(self.members.values())
        
        elif task_type == "coding":
            # Prefer models with function calling
            candidates = self.get_by_capability(supports_function_calling=True)
        
        else:
            # Default to primary
            candidates = [self.get_primary()] if self.get_primary() else []
        
        if not candidates:
            # Fall back to any enabled model
            return await self.generate_with_fallback(prompt, system, **kwargs)
        
        # Try first candidate
        try:
            response = await candidates[0].generate(prompt, system, **kwargs)
            llm_id = next(
                (id for id, provider in self.members.items() if provider == candidates[0]),
                "unknown"
            )
            return response, llm_id
        except Exception as e:
            # Fallback
            return await self.generate_with_fallback(prompt, system, **kwargs)
    
    def _get_next_enabled_id(self) -> Optional[str]:
        """Get the next enabled LLM ID."""
        for llm_id, config in self.configs.items():
            if config.enabled:
                return llm_id
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize team to dictionary."""
        return {
            "members": [config.to_dict() for config in self.configs.values()],
            "primary_id": self._primary_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMTeam':
        """Deserialize team from dictionary."""
        team = cls()
        
        for member_data in data.get("members", []):
            config = LLMConfig.from_dict(member_data)
            team.add_member(config)
        
        if primary := data.get("primary_id"):
            team.set_primary(primary)
        
        return team


# Global team instance
_global_team: Optional[LLMTeam] = None


def get_llm_team() -> LLMTeam:
    """Get the global LLM team instance."""
    global _global_team
    if _global_team is None:
        _global_team = LLMTeam()
    return _global_team


def initialize_team_from_config(team_data: Dict[str, Any]) -> None:
    """Initialize global team from configuration."""
    global _global_team
    _global_team = LLMTeam.from_dict(team_data)
