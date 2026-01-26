"""Quick demo of model manager capabilities."""
import asyncio
from pathlib import Path
from nico.ai.model_manager import get_model_manager


async def demo():
    """Show off the model manager."""
    manager = get_model_manager()
    
    print("🤖 OLLAMA MODEL MANAGER DEMO\n")
    
    # Demo 1: Character name suggestions
    print("1️⃣  Character Name Autocomplete")
    print("-" * 40)
    
    prefixes = ["Captain Elara", "Lord Vol", "Dr. Sarah"]
    for prefix in prefixes:
        suggestion = await manager.suggest_autocomplete(
            "character_name",
            prefix,
            context={"genre": "Science Fiction"}
        )
        if suggestion:
            print(f"   '{prefix}' → '{prefix}{suggestion}'")
        else:
            print(f"   '{prefix}' (no suggestion)")
    
    # Demo 2: Description continuation
    print("\n2️⃣  Description Continuation")
    print("-" * 40)
    
    starts = [
        "The ancient castle stood",
        "In the darkness of space",
        "She walked into the tavern"
    ]
    
    for start in starts:
        suggestion = await manager.suggest_autocomplete(
            "description",
            start,
            context={"genre": "Fantasy"}
        )
        if suggestion:
            print(f"   '{start}'")
            print(f"   → '{start} {suggestion}'\n")
    
    # Demo 3: Vision analysis
    print("3️⃣  Vision Model Analysis")
    print("-" * 40)
    
    portraits = list(Path("media/portraits").glob("*.png"))
    if portraits:
        test_image = portraits[0]
        print(f"   Analyzing: {test_image.name}")
        
        # Quick description
        desc = await manager.analyze_image(
            str(test_image),
            "Describe this character portrait in one sentence.",
            temperature=0.5
        )
        print(f"   Description: {desc}\n")
        
        # Approval test
        print("   Testing approval system...")
        approved, reason = await manager.approve_image(
            str(test_image),
            "A medieval fantasy character",
            criteria="Must show clear facial features"
        )
        status = "✓ APPROVED" if approved else "✗ REJECTED"
        print(f"   {status}: {reason}")
    else:
        print("   No portrait images found")
    
    # Demo 4: Direct text generation
    print("\n4️⃣  Creative Text Generation")
    print("-" * 40)
    
    result = await manager.generate_text(
        "Write a dramatic one-sentence introduction for a villain.",
        system="You are a creative writing assistant for storytelling.",
        temperature=0.9,
        max_tokens=50
    )
    print(f"   Villain intro: {result}")
    
    print("\n✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
