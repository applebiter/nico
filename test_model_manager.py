"""Test the Ollama model manager."""
import asyncio
import sys
from pathlib import Path

# Add the nico module to path
sys.path.insert(0, str(Path(__file__).parent))

from nico.ai.model_manager import get_model_manager


async def main():
    """Test the model manager functionality."""
    manager = get_model_manager()
    
    print("=" * 60)
    print("OLLAMA MODEL MANAGER TEST")
    print("=" * 60)
    
    # Test 1: Check Ollama availability
    print("\n1. Checking Ollama service...")
    available = await manager.check_ollama_available()
    if not available:
        print("❌ Ollama service not running!")
        print("   Start it with: ollama serve")
        return
    print("✓ Ollama service is running")
    
    # Test 2: List available models
    print("\n2. Listing available models...")
    models = await manager.list_models()
    if not models:
        print("❌ No models found!")
        print("   Install models with:")
        print("   ollama pull qwen2.5:4b")
        print("   ollama pull qwen2-vl:4b")
        return
    
    print(f"✓ Found {len(models)} models:")
    for model in models:
        marker = "→ " if model in [manager.text_model, manager.vision_model] else "  "
        print(f"  {marker}{model}")
    
    # Check if required models are available
    text_available = any(manager.text_model in m for m in models)
    vision_available = any(manager.vision_model in m for m in models)
    
    if not text_available:
        print(f"\n⚠️  Text model '{manager.text_model}' not found")
        print(f"   Install with: ollama pull {manager.text_model}")
    
    if not vision_available:
        print(f"\n⚠️  Vision model '{manager.vision_model}' not found")
        print(f"   Install with: ollama pull {manager.vision_model}")
    
    # Test 3: Text generation (if available)
    if text_available:
        print(f"\n3. Testing text generation ({manager.text_model})...")
        try:
            result = await manager.generate_text(
                "Write a one-sentence character description for a wizard.",
                temperature=0.8,
                max_tokens=50
            )
            print(f"✓ Generated: {result[:100]}...")
            print(f"  Current model: {manager.current_model}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 4: Autocomplete suggestions
    if text_available:
        print("\n4. Testing autocomplete suggestions...")
        try:
            suggestion = await manager.suggest_autocomplete(
                "character_name",
                "Captain Elara",
                context={"genre": "Science Fiction"}
            )
            if suggestion:
                print(f"✓ Suggestion: 'Captain Elara{suggestion}'")
            else:
                print("✓ No suggestion (text too complete)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        try:
            suggestion = await manager.suggest_autocomplete(
                "description",
                "The ancient castle stood on a cliff,",
                context={"genre": "Fantasy"}
            )
            if suggestion:
                print(f"✓ Suggestion: '...{suggestion}'")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 5: Vision model (if available and image exists)
    if vision_available:
        print(f"\n5. Testing vision analysis ({manager.vision_model})...")
        
        # Look for a test image
        test_images = [
            Path("media/portraits").glob("*.png"),
            Path("media/portraits").glob("*.jpg"),
            Path("media").glob("*.png"),
            Path("media").glob("*.jpg"),
        ]
        
        test_image = None
        for pattern in test_images:
            for img in pattern:
                if img.is_file():
                    test_image = img
                    break
            if test_image:
                break
        
        if test_image:
            try:
                print(f"  Using image: {test_image}")
                result = await manager.analyze_image(
                    str(test_image),
                    "Describe this image briefly.",
                    temperature=0.3
                )
                print(f"✓ Analysis: {result[:150]}...")
                print(f"  Current model: {manager.current_model}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("  ⚠️  No test image found in media/ directory")
            print("     Add an image to test vision capabilities")
    
    # Test 6: Model switching
    if text_available and vision_available:
        print("\n6. Testing model switching...")
        try:
            # Switch to vision
            await manager.switch_to_vision()
            print(f"✓ Switched to vision: {manager.current_model}")
            
            # Switch back to text
            await manager.switch_to_text()
            print(f"✓ Switched to text: {manager.current_model}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Summary
    print("\nSummary:")
    print(f"  Ollama: {'✓' if available else '❌'}")
    print(f"  Text model ({manager.text_model}): {'✓' if text_available else '❌'}")
    print(f"  Vision model ({manager.vision_model}): {'✓' if vision_available else '❌'}")
    
    if not text_available or not vision_available:
        print("\nTo install missing models:")
        if not text_available:
            print(f"  ollama pull {manager.text_model}")
        if not vision_available:
            print(f"  ollama pull {manager.vision_model}")


if __name__ == "__main__":
    asyncio.run(main())
