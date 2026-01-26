"""Comprehensive demo of all AI features."""
import asyncio
from pathlib import Path
from nico.ai.model_manager import get_model_manager


async def demo_all_features():
    """Demonstrate all AI model manager features."""
    manager = get_model_manager()
    
    print("🚀 NICO AI FEATURES COMPREHENSIVE DEMO")
    print("=" * 70)
    
    # Feature 1: Autocomplete
    print("\n📝 FEATURE 1: TEXT FIELD AUTOCOMPLETE")
    print("-" * 70)
    print("Demo: Real-time suggestions as you type in character fields\n")
    
    examples = [
        ("character_name", "Captain Mar", "Science Fiction"),
        ("description", "The old wizard walked through the", "Fantasy"),
        ("occupation", "Senior Softw", "Modern"),
        ("dialogue", "She looked him in the eye and said,", "Drama"),
    ]
    
    for field_type, text, genre in examples:
        suggestion = await manager.suggest_autocomplete(
            field_type, text, context={"genre": genre}
        )
        if suggestion:
            print(f"  {field_type:20s} '{text}' → '{suggestion[:50]}'")
    
    # Feature 2: Vision Analysis
    print("\n\n🖼️  FEATURE 2: IMAGE ANALYSIS")
    print("-" * 70)
    
    portraits = list(Path("media/portraits").glob("*.png"))[:3]
    if portraits:
        print(f"Analyzing {len(portraits)} character portraits:\n")
        
        for i, portrait in enumerate(portraits, 1):
            desc = await manager.analyze_image(
                str(portrait),
                "Describe this character in one sentence.",
                temperature=0.5
            )
            print(f"  {i}. {portrait.name}")
            print(f"     → {desc}\n")
    else:
        print("  No portrait images found in media/portraits/\n")
    
    # Feature 3: Image Approval
    print("\n✅ FEATURE 3: AUTOMATED IMAGE APPROVAL")
    print("-" * 70)
    
    if portraits:
        test_portrait = portraits[0]
        print(f"Testing approval for: {test_portrait.name}\n")
        
        approved, reason = await manager.approve_image(
            str(test_portrait),
            "A heroic fantasy character with clear facial features",
            criteria="Must show face clearly, appropriate for fantasy setting"
        )
        
        status = "✅ APPROVED" if approved else "❌ REJECTED"
        print(f"  Status: {status}")
        print(f"  Reason: {reason}\n")
    
    # Feature 4: Creative Generation
    print("\n🎨 FEATURE 4: CREATIVE TEXT GENERATION")
    print("-" * 70)
    print("Generating story elements:\n")
    
    prompts = [
        ("Villain intro", "Write one dramatic sentence introducing a villain."),
        ("Scene opening", "Write the opening sentence of a mystery scene."),
        ("Character quirk", "Describe an unusual character trait in one sentence."),
    ]
    
    for label, prompt in prompts:
        result = await manager.generate_text(
            prompt,
            system="You are a creative writing assistant. Be concise and vivid.",
            temperature=0.9,
            max_tokens=60
        )
        print(f"  {label:15s} → {result}\n")
    
    # Feature 5: Model Management
    print("\n🔄 FEATURE 5: HOT MODEL SWAPPING")
    print("-" * 70)
    print("Demonstrating efficient VRAM management:\n")
    
    print(f"  Current model: {manager.current_model or 'None loaded'}")
    
    # Switch to text
    await manager.switch_to_text()
    print(f"  After text switch: {manager.current_model}")
    
    # Switch to vision
    await manager.switch_to_vision()
    print(f"  After vision switch: {manager.current_model}")
    
    # Back to text
    await manager.switch_to_text()
    print(f"  Back to text: {manager.current_model}")
    
    # Feature 6: Context-Aware Suggestions
    print("\n\n🎯 FEATURE 6: CONTEXT-AWARE AUTOCOMPLETE")
    print("-" * 70)
    print("Same text, different genres:\n")
    
    text = "The hero raised their sword and"
    
    for genre in ["Fantasy", "Science Fiction", "Horror", "Romance"]:
        suggestion = await manager.suggest_autocomplete(
            "description",
            text,
            context={"genre": genre}
        )
        if suggestion:
            print(f"  {genre:20s} → '{suggestion[:60]}'")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("✨ DEMO COMPLETE!")
    print("=" * 70)
    print("\nINTEGRATION STATUS:")
    print("  ✓ Autocomplete: AutocompleteLineEdit, AutocompleteTextEdit")
    print("  ✓ Image Approval: ImageApprovalDialog, BatchImageApprovalWidget")
    print("  ✓ Model Management: Hot-swapping between granite4:3b and ministral-3:3b")
    print("  ✓ Character Dialog: Physical description field has AI autocomplete")
    print("\nNEXT STEPS:")
    print("  → Add autocomplete to more fields (occupation, motivation, etc.)")
    print("  → Integrate ImageApprovalDialog into ComfyUI workflow")
    print("  → Add tool calling for world-building queries")
    print("  → Create scene content generation with template interpolation")


if __name__ == "__main__":
    asyncio.run(demo_all_features())
