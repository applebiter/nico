"""Style transfer workflow for visual continuity across generated images."""
import json
import random
from pathlib import Path
from typing import Optional


class StyleTransferWorkflow:
    """Manages SDXL Revision workflow for style-consistent image generation.
    
    This workflow is perfect for:
    - Maintaining location aesthetics across multiple scenes
    - Keeping character appearance consistent
    - Combining character + location with unified visual style
    """
    
    def __init__(self, workflow_path: str = "comfyui_presets/sdxl_revision_text_prompts.json"):
        self.workflow_path = Path(workflow_path)
        with open(self.workflow_path) as f:
            self.template = json.load(f)
    
    def generate(
        self,
        prompt: str,
        reference_image_1: str,
        reference_image_2: str,
        negative_prompt: str = "text, watermark, blurry, low quality",
        width: int = 1920,
        height: int = 1080,
        steps: int = 26,
        cfg: float = 8.0,
        style_strength: float = 0.75,
        seed: Optional[int] = None,
        output_prefix: str = "style_transfer"
    ) -> dict:
        """Generate an image with style transfer from two reference images.
        
        Args:
            prompt: Text description of what to generate
            reference_image_1: Path to first reference image (e.g., character portrait)
            reference_image_2: Path to second reference image (e.g., location)
            negative_prompt: What to avoid in the generation
            width: Output width in pixels (default: 1920)
            height: Output height in pixels (default: 1080)
            steps: Sampling steps (more = better quality, slower)
            cfg: Classifier-free guidance (how closely to follow prompt)
            style_strength: How much style to transfer (0.0-1.0)
            seed: Random seed for reproducibility
            output_prefix: Prefix for saved images
        
        Returns:
            Modified workflow dict ready for ComfyUI
        
        Example:
            # Keep character look consistent across scenes
            workflow = StyleTransferWorkflow()
            result = workflow.generate(
                prompt="A brave knight standing in a grand castle hall",
                reference_image_1="portraits/knight_001.png",  # Character reference
                reference_image_2="locations/castle_hall.png",  # Location reference
                style_strength=0.75
            )
        """
        # Clone template
        workflow = json.loads(json.dumps(self.template))
        
        # Generate seed if not provided
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        
        # Update KSampler (node 3)
        workflow["3"]["inputs"]["seed"] = seed
        workflow["3"]["inputs"]["steps"] = steps
        workflow["3"]["inputs"]["cfg"] = cfg
        
        # Update latent dimensions (node 5)
        workflow["5"]["inputs"]["width"] = width
        workflow["5"]["inputs"]["height"] = height
        
        # Update positive prompt (node 6)
        workflow["6"]["inputs"]["text"] = prompt
        
        # Update negative prompt (node 7)
        workflow["7"]["inputs"]["text"] = negative_prompt
        
        # Update reference images (nodes 34 and 38)
        workflow["34"]["inputs"]["image"] = reference_image_1
        workflow["38"]["inputs"]["image"] = reference_image_2
        
        # Update style strength for both unCLIP nodes (19 and 37)
        workflow["19"]["inputs"]["strength"] = style_strength
        workflow["37"]["inputs"]["strength"] = style_strength
        
        # Update output prefix (node 9)
        workflow["9"]["inputs"]["filename_prefix"] = output_prefix
        
        return workflow
    
    def generate_character_in_location(
        self,
        character_name: str,
        character_portrait: str,
        location_name: str,
        location_image: str,
        action: str,
        style_strength: float = 0.75,
        **kwargs
    ) -> dict:
        """Generate a character in a location with consistent visual style.
        
        Args:
            character_name: Name of the character
            character_portrait: Path to character portrait reference
            location_name: Name/description of the location
            location_image: Path to location reference image
            action: What the character is doing
            style_strength: How much to preserve reference styles
            **kwargs: Additional arguments for generate()
        
        Example:
            workflow.generate_character_in_location(
                character_name="Sir Galahad",
                character_portrait="portraits/galahad.png",
                location_name="the throne room",
                location_image="locations/throne_room.png",
                action="kneeling before the king"
            )
        """
        prompt = f"{character_name} {action} in {location_name}"
        
        return self.generate(
            prompt=prompt,
            reference_image_1=character_portrait,
            reference_image_2=location_image,
            style_strength=style_strength,
            output_prefix=f"{character_name}_{location_name}".replace(" ", "_"),
            **kwargs
        )
    
    def generate_location_variant(
        self,
        location_name: str,
        base_location_image: str,
        style_reference_image: str,
        variation_prompt: str,
        style_strength: float = 0.8,
        **kwargs
    ) -> dict:
        """Generate a variation of a location while maintaining visual style.
        
        Args:
            location_name: Name of the location
            base_location_image: Original location image
            style_reference_image: Additional style reference (can be same or different)
            variation_prompt: How to vary the location
            style_strength: Higher = more consistent with references
            **kwargs: Additional arguments for generate()
        
        Example:
            # Generate night version of a location
            workflow.generate_location_variant(
                location_name="castle courtyard",
                base_location_image="locations/courtyard_day.png",
                style_reference_image="locations/courtyard_day.png",
                variation_prompt="the same castle courtyard at night, moonlit, torches"
            )
        """
        return self.generate(
            prompt=f"{location_name}, {variation_prompt}",
            reference_image_1=base_location_image,
            reference_image_2=style_reference_image,
            style_strength=style_strength,
            output_prefix=f"{location_name}_variant".replace(" ", "_"),
            **kwargs
        )
    
    def generate_multi_character_scene(
        self,
        scene_description: str,
        character_1_portrait: str,
        character_2_portrait: str,
        location_context: Optional[str] = None,
        style_strength: float = 0.7,
        **kwargs
    ) -> dict:
        """Generate a scene with multiple characters maintaining their looks.
        
        Args:
            scene_description: Full scene description
            character_1_portrait: First character reference
            character_2_portrait: Second character reference
            location_context: Optional location description
            style_strength: Balance between references and new generation
            **kwargs: Additional arguments for generate()
        
        Example:
            workflow.generate_multi_character_scene(
                scene_description="Sir Galahad and Lady Eleanor dancing at the ball",
                character_1_portrait="portraits/galahad.png",
                character_2_portrait="portraits/eleanor.png",
                location_context="in a grand ballroom"
            )
        """
        prompt = scene_description
        if location_context:
            prompt += f" {location_context}"
        
        return self.generate(
            prompt=prompt,
            reference_image_1=character_1_portrait,
            reference_image_2=character_2_portrait,
            style_strength=style_strength,
            output_prefix="multi_character_scene",
            **kwargs
        )
    
    def save_workflow(self, workflow: dict, output_path: str):
        """Save modified workflow to file."""
        with open(output_path, 'w') as f:
            json.dump(workflow, f, indent=2)


# Example usage
if __name__ == "__main__":
    workflow_gen = StyleTransferWorkflow()
    
    print("🎨 Style Transfer Workflow Examples")
    print("=" * 60)
    
    # Example 1: Character in location
    print("\n1. Character in Location (Visual Continuity)")
    result1 = workflow_gen.generate_character_in_location(
        character_name="Sir Galahad",
        character_portrait="portraits/knight_001.png",
        location_name="the grand throne room",
        location_image="locations/throne_room.png",
        action="kneeling before the king",
        style_strength=0.75
    )
    print(f"   Prompt: {result1['6']['inputs']['text']}")
    print(f"   References: {result1['34']['inputs']['image']} + {result1['38']['inputs']['image']}")
    print(f"   Style strength: {result1['19']['inputs']['strength']}")
    
    # Example 2: Location variant (day → night)
    print("\n2. Location Variant (Same Place, Different Time)")
    result2 = workflow_gen.generate_location_variant(
        location_name="castle courtyard",
        base_location_image="locations/courtyard_day.png",
        style_reference_image="locations/courtyard_day.png",
        variation_prompt="at night with moonlight and torches",
        style_strength=0.85  # High strength for consistency
    )
    print(f"   Prompt: {result2['6']['inputs']['text']}")
    print(f"   Style strength: {result2['19']['inputs']['strength']}")
    
    # Example 3: Multi-character scene
    print("\n3. Multi-Character Scene")
    result3 = workflow_gen.generate_multi_character_scene(
        scene_description="A knight and wizard discussing strategy",
        character_1_portrait="portraits/knight_001.png",
        character_2_portrait="portraits/wizard_001.png",
        location_context="in a war room with maps",
        style_strength=0.7
    )
    print(f"   Prompt: {result3['6']['inputs']['text']}")
    print(f"   Character refs: {result3['34']['inputs']['image']} + {result3['38']['inputs']['image']}")
    
    # Example 4: Custom generation
    print("\n4. Custom Generation")
    result4 = workflow_gen.generate(
        prompt="An epic battle scene with dragons and knights",
        reference_image_1="scenes/battle_ref.png",
        reference_image_2="scenes/dragon_ref.png",
        style_strength=0.6,  # Lower for more freedom
        width=2560,
        height=1440,
        steps=30,
        cfg=9.0
    )
    print(f"   Dimensions: {result4['5']['inputs']['width']}x{result4['5']['inputs']['height']}")
    print(f"   Steps: {result4['3']['inputs']['steps']}")
    
    print("\n" + "=" * 60)
    print("✨ Workflow templates ready for ComfyUI!")
    print("\nUse cases:")
    print("  • Maintain character appearance across multiple scenes")
    print("  • Keep location aesthetics consistent")
    print("  • Combine character + location with unified style")
    print("  • Generate variations (day/night, weather, seasons)")
    print("  • Multi-character scenes with individual consistency")
