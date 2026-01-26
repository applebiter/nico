"""Test tool calling with granite4:3b and ministral-3:3b."""
import asyncio
import json
from nico.ai.model_manager import get_model_manager


# Define some example tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_character_traits",
            "description": "Get random character traits for story generation",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of traits to generate"
                    },
                    "trait_type": {
                        "type": "string",
                        "enum": ["personality", "physical", "background"],
                        "description": "Type of traits to generate"
                    }
                },
                "required": ["count"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_location",
            "description": "Generate a fictional location description",
            "parameters": {
                "type": "object",
                "properties": {
                    "location_type": {
                        "type": "string",
                        "enum": ["city", "wilderness", "building", "planet"],
                        "description": "Type of location"
                    },
                    "atmosphere": {
                        "type": "string",
                        "description": "Desired atmosphere or mood"
                    }
                },
                "required": ["location_type"]
            }
        }
    }
]


# Tool implementations
def get_character_traits(count: int, trait_type: str = "personality") -> dict:
    """Mock implementation of character traits."""
    traits = {
        "personality": ["brave", "cunning", "compassionate", "ruthless", "wise"],
        "physical": ["tall", "scarred", "graceful", "imposing", "delicate"],
        "background": ["orphaned", "noble", "self-taught", "military", "scholarly"]
    }
    
    selected = traits.get(trait_type, traits["personality"])[:count]
    return {
        "traits": selected,
        "count": len(selected),
        "type": trait_type
    }


def generate_location(location_type: str, atmosphere: str = "neutral") -> dict:
    """Mock implementation of location generation."""
    return {
        "name": f"{atmosphere.title()} {location_type.title()}",
        "type": location_type,
        "description": f"A {atmosphere} {location_type} that serves as the perfect setting for adventure.",
        "atmosphere": atmosphere
    }


# Tool dispatcher
def call_tool(tool_name: str, arguments: dict) -> dict:
    """Dispatch tool calls to implementations."""
    tools_map = {
        "get_character_traits": get_character_traits,
        "generate_location": generate_location
    }
    
    if tool_name in tools_map:
        try:
            result = tools_map[tool_name](**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


async def test_tool_calling():
    """Test tool calling with granite4:3b."""
    manager = get_model_manager()
    
    print("🛠️  TOOL CALLING TEST")
    print("=" * 60)
    
    # Test 1: Simple tool call request
    print("\n1️⃣  Simple Tool Call Request")
    print("-" * 60)
    
    prompt = """I need 3 personality traits for a villain character.
Use the get_character_traits function."""
    
    try:
        # Note: Ollama's tool calling might have different format
        # This tests if the model can understand and respond with tool calls
        response = await manager.generate_text(
            prompt,
            system="You are a helpful assistant with access to character generation tools. When asked to generate traits or locations, use the provided functions.",
            temperature=0.3,
            max_tokens=200,
            tools=TOOLS
        )
        
        print(f"Response: {response}")
        
        # Try to parse if it contains function call
        if "get_character_traits" in response.lower():
            print("✓ Model recognized the tool!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Multiple tool scenario
    print("\n2️⃣  Multiple Tools Available")
    print("-" * 60)
    
    prompt = """Create a brief character concept that includes:
1. The character's personality traits (use get_character_traits)
2. Their home location (use generate_location)

Be creative and combine the results into a short character description."""
    
    try:
        response = await manager.generate_text(
            prompt,
            system="You have access to character generation tools. Use them when appropriate to create rich characters.",
            temperature=0.7,
            max_tokens=300,
            tools=TOOLS
        )
        
        print(f"Response: {response[:500]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Manual tool call simulation
    print("\n3️⃣  Simulated Tool Use Workflow")
    print("-" * 60)
    
    print("Step 1: Request character traits")
    traits_result = call_tool("get_character_traits", {"count": 3, "trait_type": "personality"})
    print(f"  Tool result: {traits_result}")
    
    print("\nStep 2: Request location")
    location_result = call_tool("generate_location", {"location_type": "city", "atmosphere": "dystopian"})
    print(f"  Tool result: {location_result}")
    
    print("\nStep 3: Ask AI to synthesize")
    synthesis_prompt = f"""Create a one-paragraph character description using:
- Traits: {traits_result['result']['traits']}
- Location: {location_result['result']['name']}
- Atmosphere: {location_result['result']['atmosphere']}"""
    
    try:
        synthesis = await manager.generate_text(
            synthesis_prompt,
            system="You are a creative writing assistant. Synthesize the provided elements into a compelling character description.",
            temperature=0.8,
            max_tokens=200
        )
        
        print(f"\n✨ Generated Character:")
        print(f"  {synthesis}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Tool calling test complete!")
    print("\nNote: Ollama's tool calling support varies by model.")
    print("Granite4:3b should support structured function calling.")


if __name__ == "__main__":
    asyncio.run(test_tool_calling())
