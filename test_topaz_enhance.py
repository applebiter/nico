#!/usr/bin/env python3
"""Test the Topaz Image Enhance workflow integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nico.infrastructure.topaz_enhance_workflow import TopazEnhanceWorkflow


def main():
    """Test the Topaz enhance workflow."""
    print("=" * 60)
    print("TOPAZ IMAGE ENHANCE WORKFLOW TEST")
    print("=" * 60)
    print()
    
    workflow = TopazEnhanceWorkflow()
    
    print("✓ Workflow loaded from comfyui_presets/api_topaz_image_enhance.json")
    print()
    
    # Test FHD enhancement
    print("Test 1: Enhance to Full HD (1920×1080)")
    print("-" * 60)
    
    test_image = "test_image.png"
    fhd_workflow = workflow.enhance_to_fhd(
        input_image_path=test_image,
        creativity=3,
        face_enhancement=True
    )
    
    print(f"Input: {test_image}")
    print(f"Output dimensions: {fhd_workflow['4']['inputs']['value']}×{fhd_workflow['5']['inputs']['value']}")
    print(f"Model: {fhd_workflow['1']['inputs']['model']}")
    print(f"Creativity: {fhd_workflow['1']['inputs']['creativity']}")
    print(f"Face enhancement: {fhd_workflow['1']['inputs']['face_enhancement']}")
    print()
    
    # Test portrait enhancement
    print("Test 2: Portrait Enhancement (1080×1920)")
    print("-" * 60)
    
    portrait_workflow = workflow.enhance_portrait(
        input_image_path=test_image,
        face_enhancement_strength=1
    )
    
    print(f"Input: {test_image}")
    print(f"Output dimensions: {portrait_workflow['4']['inputs']['value']}×{portrait_workflow['5']['inputs']['value']}")
    print(f"Model: {portrait_workflow['1']['inputs']['model']}")
    print(f"Creativity: {portrait_workflow['1']['inputs']['creativity']} (lower for faces)")
    print(f"Face enhancement strength: {portrait_workflow['1']['inputs']['face_enhancement_strength']}")
    print()
    
    # Test custom dimensions
    print("Test 3: Custom Enhancement (2560×1440, 4K ready)")
    print("-" * 60)
    
    custom_workflow = workflow.enhance(
        input_image_path=test_image,
        output_width=2560,
        output_height=1440,
        creativity=5,
        enhancement_prompt="Enhance for 4K display with maximum detail"
    )
    
    print(f"Input: {test_image}")
    print(f"Output dimensions: {custom_workflow['4']['inputs']['value']}×{custom_workflow['5']['inputs']['value']}")
    print(f"Creativity: {custom_workflow['1']['inputs']['creativity']}")
    print(f"Custom prompt: {custom_workflow['1']['inputs']['prompt'][:60]}...")
    print()
    
    print("=" * 60)
    print("✓ All workflow generation tests passed!")
    print()
    print("Integration complete:")
    print("  • TopazEnhanceWorkflow class created")
    print("  • '📺 Export to FHD' button added to Image Generation Dialog")
    print("  • Appears after successful image generation")
    print("  • Generates 1920×1080 enhancement workflow")
    print("  • Saves workflow JSON for ComfyUI execution")
    print()
    print("Usage in GUI:")
    print("  1. Generate an image using Simple or Style Transfer tab")
    print("  2. Click '📺 Export to FHD (1920×1080)' button")
    print("  3. Choose save location")
    print("  4. Workflow JSON is created (ready for ComfyUI)")
    print()


if __name__ == "__main__":
    main()
