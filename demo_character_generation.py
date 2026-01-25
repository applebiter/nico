"""Demo: Generate random characters using imported world-building tables."""
from nico.application.context import get_app_context
from nico.domain.models import WorldBuildingTable, Character


def get_random_from_table(app_context, project_id: int, table_name: str) -> str:
    """Get a random item from a world-building table."""
    table = app_context._session.query(WorldBuildingTable).filter_by(
        project_id=project_id,
        table_name=table_name
    ).first()
    
    if table and table.items:
        return table.get_random_item()
    return f"[{table_name} not found]"


def generate_random_character(project_id: int, gender: str = "male") -> dict:
    """Generate a random character using world-building tables.
    
    Args:
        project_id: Project with imported tables
        gender: "male" or "female"
        
    Returns:
        Dict with character attributes
    """
    app_context = get_app_context()
    
    # Choose name tables based on gender
    if gender.lower() == "female":
        first_name_table = "generator-names.female"
    else:
        first_name_table = "generator-names.male"
    
    character = {
        "first_name": get_random_from_table(app_context, project_id, first_name_table),
        "surname": get_random_from_table(app_context, project_id, "generator-names.surnames"),
        "occupation": get_random_from_table(app_context, project_id, "characters"),
        "trait": get_random_from_table(app_context, project_id, "random_trait_generator.col1"),
        "city": get_random_from_table(app_context, project_id, "generator-names.city_of_origin"),
    }
    
    # Build full name
    character["full_name"] = f"{character['first_name']} {character['surname']}"
    
    return character


def generate_character_batch(project_id: int, count: int = 5):
    """Generate multiple random characters."""
    
    print(f"\n{'='*70}")
    print(f"GENERATING {count} RANDOM CHARACTERS")
    print('='*70)
    
    characters = []
    
    for i in range(count):
        gender = "female" if i % 2 == 0 else "male"
        char = generate_random_character(project_id, gender)
        characters.append(char)
        
        print(f"\nCharacter #{i+1} ({gender}):")
        print(f"  Name: {char['full_name']}")
        print(f"  Occupation: {char['occupation']}")
        print(f"  Trait: {char['trait']}")
        print(f"  From: {char['city']}")
    
    return characters


def show_available_options(project_id: int):
    """Show what options are available for character creation."""
    app_context = get_app_context()
    
    print(f"\n{'='*70}")
    print("AVAILABLE CHARACTER CREATION OPTIONS")
    print('='*70)
    
    options = [
        ("First Names (Male)", "generator-names.male"),
        ("First Names (Female)", "generator-names.female"),
        ("Surnames", "generator-names.surnames"),
        ("Occupations", "characters"),
        ("Cities/Origin", "generator-names.city_of_origin"),
        ("Traits", "random_trait_generator.col1"),
        ("Character Types", "random_trait_generator.it's_a_kludge!_character_trait_generator"),
    ]
    
    for label, table_name in options:
        table = app_context._session.query(WorldBuildingTable).filter_by(
            project_id=project_id,
            table_name=table_name
        ).first()
        
        if table:
            print(f"\n{label}: {len(table.items)} options")
            print(f"  Examples: {', '.join(table.items[:10])}")


def generate_character_profile(project_id: int, name: str = None, gender: str = "male") -> str:
    """Generate a full character profile text."""
    
    char = generate_random_character(project_id, gender)
    if name:
        parts = name.split()
        if len(parts) >= 2:
            char["first_name"] = parts[0]
            char["surname"] = ' '.join(parts[1:])
            char["full_name"] = name
    
    profile = f"""
CHARACTER PROFILE
{'='*70}

Name: {char['full_name']}
Origin: {char['city']}
Occupation: {char['occupation']}
Notable Trait: {char['trait']}

Background:
{char['first_name']} {char['surname']} grew up in {char['city']} and now works as 
{char['occupation']}. Known for being {char['trait'].lower()}, {char['first_name']} 
brings a unique perspective to every situation.

Potential Story Hooks:
- What challenges does {char['first_name']} face in their occupation?
- How does their {char['trait'].lower()} nature affect relationships?
- What secrets might {char['city']} hold?
"""
    return profile


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Random Character Generator using imported CSV data")
        print("\nUsage:")
        print("  python demo_character_generation.py <project_id> [options|batch|profile]")
        print("\nExamples:")
        print("  python demo_character_generation.py 1 options   # Show available options")
        print("  python demo_character_generation.py 1 batch     # Generate 5 random characters")
        print("  python demo_character_generation.py 1 profile   # Generate detailed profile")
        sys.exit(1)
    
    project_id = int(sys.argv[1])
    command = sys.argv[2] if len(sys.argv) > 2 else "batch"
    
    if command == "options":
        show_available_options(project_id)
    elif command == "profile":
        print(generate_character_profile(project_id))
    else:
        generate_character_batch(project_id, count=5)
