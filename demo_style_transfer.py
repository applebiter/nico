"""Demo: Using style transfer for visual continuity in story scenes."""
import asyncio
from pathlib import Path
from nico.infrastructure.style_transfer_workflow import StyleTransferWorkflow
from nico.infrastructure.comfyui_service import ComfyUIService


async def demo_visual_continuity():
    """Demonstrate maintaining visual continuity across multiple generated images."""
    
    workflow_gen = StyleTransferWorkflow()
    
    print("🎨 VISUAL CONTINUITY DEMO")
    print("=" * 70)
    print("Using style transfer to maintain consistent look across scenes\n")
    
    # Find some existing portraits to use as references
    portraits_dir = Path("media/portraits")
    portraits = list(portraits_dir.glob("*.png"))
    
    if len(portraits) < 2:
        print("❌ Need at least 2 portrait images in media/portraits/")
        return
    
    print(f"Found {len(portraits)} portraits to use as references\n")
    
    # Scenario 1: Character in different settings
    print("📖 SCENARIO 1: Same Character, Different Locations")
    print("-" * 70)
    
    character_ref = portraits[0]
    print(f"Character reference: {character_ref.name}\n")
    
    scenes = [
        {
            "location": "medieval castle throne room",
            "action": "standing before the king",
            "style_ref": character_ref,  # Use same for consistent character look
        },
        {
            "location": "dark forest at night",
            "action": "exploring with a torch",
            "style_ref": character_ref,
        },
        {
            "location": "bustling medieval marketplace",
            "action": "browsing the stalls",
            "style_ref": character_ref,
        }
    ]
    
    for i, scene in enumerate(scenes, 1):
        workflow = workflow_gen.generate(
            prompt=f"A brave adventurer {scene['action']} in {scene['location']}, fantasy art style",
            reference_image_1=str(character_ref),
            reference_image_2=str(scene['style_ref']),
            style_strength=0.8,  # High strength for character consistency
            output_prefix=f"scene_{i}",
            width=1920,
            height=1080,
            steps=26
        )
        
        print(f"  Scene {i}: {scene['location']}")
        print(f"    Prompt: '{workflow['6']['inputs']['text']}'")
        print(f"    Style strength: {workflow['19']['inputs']['strength']}")
        print(f"    Ready to send to ComfyUI\n")
    
    # Scenario 2: Multiple characters meeting
    print("\n📖 SCENARIO 2: Multiple Characters in One Scene")
    print("-" * 70)
    
    if len(portraits) >= 2:
        char1 = portraits[0]
        char2 = portraits[1]
        
        workflow = workflow_gen.generate_multi_character_scene(
            scene_description="Two heroes meeting at a crossroads",
            character_1_portrait=str(char1),
            character_2_portrait=str(char2),
            location_context="under a ancient oak tree, sunset lighting",
            style_strength=0.75
        )
        
        print(f"  Character 1: {char1.name}")
        print(f"  Character 2: {char2.name}")
        print(f"  Prompt: '{workflow['6']['inputs']['text']}'")
        print(f"  Style strength: {workflow['19']['inputs']['strength']}\n")
    
    # Scenario 3: Location variants (same place, different conditions)
    print("\n📖 SCENARIO 3: Location Variants (Time/Weather Changes)")
    print("-" * 70)
    
    location_ref = character_ref  # Can reuse any image as location reference
    
    variants = [
        "at dawn with morning mist",
        "during a thunderstorm with lightning",
        "at sunset with golden hour lighting",
        "at night under a full moon",
    ]
    
    for variant in variants:
        workflow = workflow_gen.generate_location_variant(
            location_name="ancient stone bridge over a river",
            base_location_image=str(location_ref),
            style_reference_image=str(location_ref),
            variation_prompt=variant,
            style_strength=0.85,  # Very high for location consistency
        )
        
        print(f"  Variant: {variant}")
        print(f"    Prompt: '{workflow['6']['inputs']['text'][:60]}...'")
    
    print("\n" + "=" * 70)
    print("✨ BENEFITS OF STYLE TRANSFER WORKFLOW:")
    print("=" * 70)
    print("""
1. CHARACTER CONSISTENCY
   - Same character looks similar across all scenes
   - Maintains facial features, clothing style, color palette
   - Viewers recognize the character instantly

2. LOCATION CONTINUITY
   - Same location can be shown at different times/weather
   - Architectural style remains consistent
   - Creates believable world-building

3. UNIFIED VISUAL STYLE
   - All images share cohesive aesthetic
   - Color grading stays consistent
   - Art style (realistic/painterly/anime) maintained

4. MULTI-CHARACTER SCENES
   - Combine two character references
   - Both characters maintain their individual looks
   - Perfect for dialogue scenes, confrontations, partnerships

5. STORY COHERENCE
   - Readers/viewers see visual consistency
   - Less cognitive load to follow the story
   - More immersive experience
    """)
    
    print("WORKFLOW PARAMETERS:")
    print("  • style_strength: 0.6-0.7 = More creative freedom")
    print("  • style_strength: 0.75-0.8 = Balanced (recommended)")
    print("  • style_strength: 0.85-0.95 = Maximum consistency")
    
    print("\nRECOMMENDED APPROACH:")
    print("  1. Generate character portrait → Save as reference")
    print("  2. Generate location render → Save as reference")
    print("  3. Use style_transfer_workflow to combine them")
    print("  4. Generate multiple scenes with same references")
    print("  5. Build a visually coherent story sequence")


if __name__ == "__main__":
    asyncio.run(demo_visual_continuity())
