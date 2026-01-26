"""Topaz Image Enhance workflow for upscaling and enhancing generated images."""
import json
from pathlib import Path
from typing import Dict, Any, Optional


class TopazEnhanceWorkflow:
    """Wrapper for Topaz Image Enhance ComfyUI workflow.
    
    This workflow uses Topaz Photo AI to enhance and upscale images,
    perfect for creating Full HD (1920×1080) exports from generated images.
    """
    
    def __init__(self, workflow_path: str = "comfyui_presets/api_topaz_image_enhance.json"):
        self.workflow_path = Path(workflow_path)
        with open(self.workflow_path) as f:
            self.template = json.load(f)
    
    def enhance(
        self,
        input_image_path: str,
        output_width: int = 1920,
        output_height: int = 1080,
        model: str = "Reimagine",
        creativity: int = 3,
        face_enhancement: bool = True,
        face_enhancement_strength: int = 1,
        enhancement_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an enhancement workflow for the given image.
        
        Args:
            input_image_path: Path to the image to enhance
            output_width: Target width (default: 1920 for FHD)
            output_height: Target height (default: 1080 for FHD)
            model: Topaz model to use ("Reimagine", "Enhance", etc.)
            creativity: Creativity level 0-10 (default: 3)
            face_enhancement: Enable face enhancement
            face_enhancement_strength: Face enhancement strength 0-1
            enhancement_prompt: Optional custom prompt describing desired enhancements
            
        Returns:
            Complete workflow dictionary ready for ComfyUI
        """
        # Deep copy the template
        workflow = json.loads(json.dumps(self.template))
        
        # Update input image path (Node 2)
        workflow["2"]["inputs"]["image"] = str(input_image_path)
        
        # Update output dimensions (Nodes 4 and 5)
        workflow["4"]["inputs"]["value"] = output_width
        workflow["5"]["inputs"]["value"] = output_height
        
        # Update Topaz enhance settings (Node 1)
        workflow["1"]["inputs"]["model"] = model
        workflow["1"]["inputs"]["creativity"] = creativity
        workflow["1"]["inputs"]["face_enhancement"] = face_enhancement
        workflow["1"]["inputs"]["face_enhancement_strength"] = face_enhancement_strength
        
        # Update enhancement prompt if provided
        if enhancement_prompt:
            workflow["1"]["inputs"]["prompt"] = enhancement_prompt
        else:
            # Default prompt for generated images
            workflow["1"]["inputs"]["prompt"] = (
                "Enhance this AI-generated image. Increase sharpness and clarity, "
                "enhance fine details, improve color vibrancy, and refine textures. "
                "Maintain the artistic style while making the image crisper and more defined."
            )
        
        return workflow
    
    def enhance_to_fhd(
        self,
        input_image_path: str,
        creativity: int = 3,
        face_enhancement: bool = True
    ) -> Dict[str, Any]:
        """Quick method to enhance to Full HD 16:9 (1920×1080).
        
        Args:
            input_image_path: Path to the image to enhance
            creativity: Creativity level 0-10
            face_enhancement: Enable face enhancement
            
        Returns:
            Workflow configured for FHD output
        """
        return self.enhance(
            input_image_path=input_image_path,
            output_width=1920,
            output_height=1080,
            creativity=creativity,
            face_enhancement=face_enhancement
        )
    
    def enhance_portrait(
        self,
        input_image_path: str,
        output_width: int = 1080,
        output_height: int = 1920,
        face_enhancement_strength: int = 1
    ) -> Dict[str, Any]:
        """Enhance a portrait image with strong face enhancement.
        
        Args:
            input_image_path: Path to portrait image
            output_width: Target width (default: 1080)
            output_height: Target height (default: 1920 for vertical)
            face_enhancement_strength: Strength 0-1 (default: 1 for max)
            
        Returns:
            Workflow optimized for portrait enhancement
        """
        return self.enhance(
            input_image_path=input_image_path,
            output_width=output_width,
            output_height=output_height,
            creativity=2,  # Lower creativity for faces
            face_enhancement=True,
            face_enhancement_strength=face_enhancement_strength,
            enhancement_prompt=(
                "Enhance this portrait image. Sharpen facial features, enhance skin texture naturally, "
                "improve eye clarity and detail, refine hair details, and enhance overall facial definition. "
                "Preserve natural skin tones and maintain realistic appearance."
            )
        )
