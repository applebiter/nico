"""Demonstration of fully enhanced character dialog with all CSV data."""
from nico.application.context import get_app_context
from nico.domain.models import WorldBuildingTable


def show_available_data(project_id: int = 1):
    """Show what data is available for character generation."""
    app_context = get_app_context()
    
    print("\n" + "="*70)
    print("ENHANCED CHARACTER DIALOG - AVAILABLE DATA")
    print("="*70)
    
    data_sources = [
        ("First Names", "generator-names.male", "226 male names"),
        ("First Names", "generator-names.female", "226 female names"),
        ("Surnames", "generator-names.surnames", "245 surnames"),
        ("Hometowns", "generator-names.city_of_origin", "601 authentic city names"),
        ("Occupations", "characters", "5,798 government occupations"),
        ("Character Types", "character.types", "9 archetypes"),
        ("Motivations", "character.motivations", "23 core motivations"),
        ("Personality Traits", "random_trait_generator.col1", "24 traits"),
        ("Wounds/Traumas", "character.wounds", "117 emotional wounds"),
    ]
    
    for label, table_name, description in data_sources:
        table = app_context._session.query(WorldBuildingTable).filter_by(
            project_id=project_id,
            table_name=table_name
        ).first()
        
        if table:
            print(f"\n✓ {label}: {description}")
            samples = table.items[:5]
            print(f"  Samples: {', '.join(samples)}")
    
    print("\n" + "="*70)
    print("TOTAL DATA AVAILABLE FOR CHARACTER CREATION")
    print("="*70)
    print(f"  • Names: 697 options (452 first + 245 surnames)")
    print(f"  • Locations: 601 cities")
    print(f"  • Occupations: 5,798 options")
    print(f"  • Psychology: 173 options (9 types + 23 motivations + 24 traits + 117 wounds)")
    print(f"\n  GRAND TOTAL: 7,269 data points!")
    print("="*70)


def generate_complete_character(project_id: int = 1, gender: str = "female"):
    """Generate a complete random character using ALL available data."""
    app_context = get_app_context()
    
    def get_random(table_name: str) -> str:
        table = app_context._session.query(WorldBuildingTable).filter_by(
            project_id=project_id,
            table_name=table_name
        ).first()
        return table.get_random_item() if table else "[not found]"
    
    # Build character
    first_name_table = f"generator-names.{gender}"
    
    character = {
        "first_name": get_random(first_name_table),
        "surname": get_random("generator-names.surnames"),
        "hometown": get_random("generator-names.city_of_origin"),
        "occupation": get_random("characters"),
        "character_type": get_random("character.types"),
        "motivation": get_random("character.motivations"),
        "trait": get_random("random_trait_generator.col1"),
        "wound": get_random("character.wounds"),
    }
    
    character["full_name"] = f"{character['first_name']} {character['surname']}"
    
    return character


def show_character_samples(count: int = 3):
    """Generate and display sample characters."""
    
    print("\n" + "="*70)
    print(f"SAMPLE CHARACTERS (ALL FIELDS RANDOMIZED)")
    print("="*70)
    
    genders = ["female", "male", "female"]
    
    for i in range(count):
        char = generate_complete_character(gender=genders[i % len(genders)])
        
        print(f"\n{'─'*70}")
        print(f"CHARACTER #{i+1}: {char['full_name']}")
        print('─'*70)
        print(f"  📍 Hometown:        {char['hometown']}")
        print(f"  💼 Occupation:      {char['occupation']}")
        print(f"  🎭 Character Type:  {char['character_type']}")
        print(f"  🎯 Motivation:      {char['motivation']}")
        print(f"  ⭐ Personality:     {char['trait']}")
        print(f"  💔 Primary Wound:   {char['wound']}")
        print()
        print(f"  Story Hook:")
        print(f"  {char['first_name']}, a {char['trait'].lower()} {char['character_type']} from")
        print(f"  {char['hometown']}, works as {char['occupation']}. Driven by")
        print(f"  {char['motivation'].lower()}, they struggle with {char['wound'].lower()}.")


def show_dialog_features():
    """Show what features are in the enhanced dialog."""
    
    print("\n" + "="*70)
    print("CHARACTER DIALOG FEATURES")
    print("="*70)
    
    features = [
        ("BASIC INFO Tab", [
            "• First Name: 452 options with search + 🎲 random",
            "• Last Name: 245 surnames with search + 🎲 random",
            "• Physical description (plain text)"
        ]),
        ("IDENTITY Tab", [
            "• Gender, Sex, Ethnicity, Race",
            "• Tribe/Clan, Nationality, Religion",
            "• Hometown: 601 cities with search + 🎲 random"
        ]),
        ("LIFE DETAILS Tab", [
            "• Occupation: 5,798 options with search + 🎲 random",
            "• Education, Marital Status",
            "• Date of Birth, Date of Death"
        ]),
        ("PSYCHOLOGY Tab", [
            "• Character Type: 9 archetypes + 🎲 random",
            "• Motivation: 23 core drives + 🎲 random",
            "• Personality Trait: 24 traits + 🎲 random",
            "• Myers-Briggs, Enneagram",
            "• Primary Wound: 117 traumas + 🎲 random",
            "• Additional wounds/notes (text area)"
        ])
    ]
    
    for tab_name, items in features:
        print(f"\n{tab_name}:")
        for item in items:
            print(f"  {item}")
    
    print("\n" + "="*70)
    print("HOW TO USE")
    print("="*70)
    print("  1. Click any dropdown → start typing to search")
    print("  2. Click 🎲 button → instant random selection")
    print("  3. Type anything → custom values always allowed")
    print("  4. Arrow keys → navigate filtered results")
    print("  5. Enter/Tab → select highlighted item")
    print("\n  Perfect for:")
    print("  • Quick NPC generation (use all 🎲 buttons!)")
    print("  • Finding authentic historical names")
    print("  • Discovering interesting occupation combinations")
    print("  • Building psychologically deep characters")
    print("="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENHANCED CHARACTER DIALOG DEMONSTRATION")
    print("Powered by your wife's CSV data collection!")
    print("="*70)
    
    show_available_data()
    show_dialog_features()
    show_character_samples(count=3)
    
    print("\n" + "="*70)
    print("TO TRY IT IN THE APP:")
    print("="*70)
    print("  1. Run: python -m nico")
    print("  2. Open a project")
    print("  3. Click 'New Character'")
    print("  4. Try the dropdown searches and 🎲 random buttons!")
    print("  5. Create an instant NPC by clicking all 🎲 buttons")
    print("="*70 + "\n")
