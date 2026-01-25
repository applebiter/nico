"""Extract useful character generation data from imported tables."""
from nico.application.context import get_app_context
from nico.domain.models import WorldBuildingTable
import csv


def extract_character_data(project_id: int):
    """Extract and organize character-related data."""
    app_context = get_app_context()
    
    # Get the big characters table with occupations
    char_table = app_context._session.query(WorldBuildingTable).filter_by(
        project_id=project_id,
        table_name="characters"
    ).first()
    
    if not char_table:
        print("Characters table not found!")
        return
    
    print("Parsing character CSV data...")
    
    # The items are actually CSV rows, let's parse them
    occupations = []
    surnames = []
    f_names = []
    m_names = []
    motivations = []
    character_types = []
    wounds = []
    
    # Parse CSV structure
    for item in char_table.items[:100]:  # First 100 to see structure
        parts = item.split(',')
        if len(parts) >= 7:
            if parts[0] and parts[0] not in surnames:
                surnames.append(parts[0])
            if parts[1] and parts[1] not in f_names:
                f_names.append(parts[1])
            if parts[2] and parts[2] not in m_names:
                m_names.append(parts[2])
            if parts[3] and parts[3] not in motivations:
                motivations.append(parts[3])
            if parts[4] and parts[4] not in character_types:
                character_types.append(parts[4])
            if parts[5] and parts[5] not in wounds:
                wounds.append(parts[5])
            if parts[6] and parts[6] not in occupations:
                occupations.append(parts[6])
    
    print(f"\nExtracted from characters table:")
    print(f"  Surnames: {len(surnames)}")
    print(f"  Female names: {len(f_names)}")
    print(f"  Male names: {len(m_names)}")
    print(f"  Motivations: {len(motivations)}")
    print(f"  Character types: {len(character_types)}")
    print(f"  Wounds: {len(wounds)}")
    print(f"  Occupations: {len(occupations)}")
    
    print(f"\nSample occupations:")
    for occ in occupations[:20]:
        print(f"  • {occ}")
    
    print(f"\nSample motivations:")
    for mot in motivations[:10]:
        print(f"  • {mot}")
    
    print(f"\nSample wounds:")
    for wound in wounds[:10]:
        print(f"  • {wound}")


def list_name_tables(project_id: int):
    """List all name-related tables."""
    app_context = get_app_context()
    
    tables = app_context._session.query(WorldBuildingTable).filter(
        WorldBuildingTable.project_id == project_id,
        WorldBuildingTable.table_name.like('%name%')
    ).all()
    
    print(f"\n{'='*70}")
    print("NAME TABLES AVAILABLE")
    print('='*70)
    
    for table in tables:
        print(f"\n{table.table_name}: {len(table.items)} items")
        print(f"  Samples: {', '.join(table.items[:10])}")


def show_useful_tables(project_id: int):
    """Show most useful tables for story generation."""
    app_context = get_app_context()
    
    useful_patterns = [
        ('names', 'Names (male, female, surnames)'),
        ('motivation', 'Character motivations'),
        ('wound', 'Character wounds/trauma'),
        ('occupation', 'Occupations/careers'),
        ('trait', 'Character traits'),
        ('plot', 'Plot ideas'),
        ('trope', 'Story tropes'),
        ('dramatic', 'Dramatic situations'),
        ('location', 'Locations/settings'),
        ('genre', 'Genre elements'),
    ]
    
    print(f"\n{'='*70}")
    print("MOST USEFUL TABLES FOR CHARACTER/STORY GENERATION")
    print('='*70)
    
    for pattern, description in useful_patterns:
        tables = app_context._session.query(WorldBuildingTable).filter(
            WorldBuildingTable.project_id == project_id,
            WorldBuildingTable.table_name.ilike(f'%{pattern}%')
        ).all()
        
        if tables:
            print(f"\n{description}:")
            for table in tables:
                print(f"  • {table.table_name}: {len(table.items)} items")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_character_data.py <project_id>")
        sys.exit(1)
    
    project_id = int(sys.argv[1])
    
    show_useful_tables(project_id)
    list_name_tables(project_id)
    extract_character_data(project_id)
