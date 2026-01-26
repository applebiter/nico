"""ComfyUI integration service for image generation."""
import json
import random
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import aiohttp
import asyncio


class ComfyUIService:
    """Service for interacting with ComfyUI API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8188", project_path: Optional[Path] = None):
        """
        Initialize ComfyUI service.
        
        Args:
            base_url: Base URL of the ComfyUI server (default: http://127.0.0.1:8188)
            project_path: Path to the current project root (for saving images)
        """
        self.base_url = base_url
        self.client_id = str(uuid.uuid4())
        self.project_path = project_path
        
        # Load the workflow template
        workflow_path = Path(__file__).parent.parent.parent / "comfyui_presets" / "image_z_image_turbo.json"
        with open(workflow_path, 'r') as f:
            self.workflow_template = json.load(f)
    
    def _prepare_workflow(self, prompt: str, width: int = 1024, height: int = 1024, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Prepare workflow with the given prompt and dimensions.
        
        Args:
            prompt: The text prompt for image generation
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed (if None, generates random seed)
            
        Returns:
            Modified workflow dictionary ready to send to ComfyUI
        """
        workflow = json.loads(json.dumps(self.workflow_template))  # Deep copy
        
        # Update the prompt in node 58
        # Add negative instructions to prevent text rendering
        prompt_with_supplement = f"{prompt}, no text"
        workflow["58"]["inputs"]["value"] = prompt_with_supplement
        
        # Update seed in node 57:3 (KSampler)
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        workflow["57:3"]["inputs"]["seed"] = seed
        
        # Update dimensions in EmptySD3LatentImage node (node 57:13)
        workflow["57:13"]["inputs"]["width"] = width
        workflow["57:13"]["inputs"]["height"] = height
        
        return workflow
    
    async def execute_workflow(
        self,
        workflow: Dict[str, Any],
        timeout: int = 120
    ) -> Optional[Path]:
        """
        Execute a pre-built workflow on ComfyUI.
        
        Args:
            workflow: The workflow dictionary to execute
            timeout: Maximum time to wait for generation in seconds
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        async with aiohttp.ClientSession() as session:
            try:
                # Queue the prompt
                prompt_data = {
                    "prompt": workflow,
                    "client_id": self.client_id
                }
                
                url = urljoin(self.base_url, "/prompt")
                async with session.post(url, json=prompt_data) as response:
                    if response.status != 200:
                        print(f"Error queueing prompt: {response.status}")
                        return None
                    
                    result = await response.json()
                    prompt_id = result.get("prompt_id")
                    
                    if not prompt_id:
                        print("No prompt_id returned")
                        return None
                
                # Wait for completion and get the image
                return await self._wait_for_completion(session, prompt_id, timeout)
                
            except aiohttp.ClientError as e:
                print(f"Error connecting to ComfyUI: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
        timeout: int = 120
    ) -> Optional[Path]:
        """
        Generate an image using ComfyUI.
        
        Args:
            prompt: The text description of the image to generate
            width: Image width in pixels
            height: Image height in pixels
            seed: Random seed for reproducibility (optional)
            timeout: Maximum time to wait for generation in seconds
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        workflow = self._prepare_workflow(prompt, width, height, seed)
        return await self.execute_workflow(workflow, timeout)
                    

    
    async def _wait_for_completion(
        self,
        session: aiohttp.ClientSession,
        prompt_id: str,
        timeout: int
    ) -> Optional[Path]:
        """
        Wait for image generation to complete and retrieve the image.
        
        Args:
            session: aiohttp session
            prompt_id: The prompt ID to check for
            timeout: Maximum time to wait
            
        Returns:
            Path to the generated image, or None if failed
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check history
            history_url = urljoin(self.base_url, f"/history/{prompt_id}")
            
            try:
                async with session.get(history_url) as response:
                    if response.status == 200:
                        history = await response.json()
                        
                        if prompt_id in history:
                            outputs = history[prompt_id].get("outputs", {})
                            
                            # Look for saved images (node 9 is SaveImage in our workflow)
                            for node_id, node_output in outputs.items():
                                if "images" in node_output:
                                    images = node_output["images"]
                                    if images:
                                        # Get the first image
                                        image_info = images[0]
                                        filename = image_info["filename"]
                                        subfolder = image_info.get("subfolder", "")
                                        
                                        # Download the image
                                        return await self._download_image(
                                            session,
                                            filename,
                                            subfolder
                                        )
            
            except Exception as e:
                print(f"Error checking history: {e}")
            
            # Wait before checking again
            await asyncio.sleep(1)
        
        print(f"Timeout waiting for image generation after {timeout}s")
        return None
    
    async def _download_image(
        self,
        session: aiohttp.ClientSession,
        filename: str,
        subfolder: str
    ) -> Optional[Path]:
        """
        Download the generated image from ComfyUI.
        
        Args:
            session: aiohttp session
            filename: Name of the image file
            subfolder: Subfolder where image is stored
            
        Returns:
            Path to the downloaded image
        """
        # Build the view URL
        params = {"filename": filename, "subfolder": subfolder, "type": "output"}
        view_url = urljoin(self.base_url, "/view")
        
        try:
            async with session.get(view_url, params=params) as response:
                if response.status == 200:
                    # Determine output directory
                    if self.project_path:
                        # Save to project's media folder
                        output_dir = self.project_path / "media" / "portraits"
                    else:
                        # Fallback to temp location
                        output_dir = Path("/tmp/nico_images")
                    
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / filename
                    
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())
                    
                    return output_path
        
        except Exception as e:
            print(f"Error downloading image: {e}")
        
        return None
    
    async def check_connection(self) -> bool:
        """
        Check if ComfyUI server is reachable.
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = urljoin(self.base_url, "/system_stats")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False


# Singleton instance
_comfyui_service: Optional[ComfyUIService] = None


def get_comfyui_service(base_url: str = "http://127.0.0.1:8188", project_path: Optional[Path] = None) -> ComfyUIService:
    """Get or create the global ComfyUI service instance."""
    global _comfyui_service
    if _comfyui_service is None:
        _comfyui_service = ComfyUIService(base_url, project_path)
    elif project_path and _comfyui_service.project_path != project_path:
        # Update project path if changed
        _comfyui_service.project_path = project_path
    return _comfyui_service
