"""Complete workflow example: CSV import → Template → Scene generation."""
from pathlib import Path
from nico.application.context import get_app_context
from nico.application.csv_importer import import_csv_to_table
from nico.domain.models import WorldBuildingTable, SceneTemplate


def create_sample_csv_files(output_dir: str = "sample_csvs"):
    """Create sample CSV files to demonstrate import."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Locations - crime scenes
    with open(output_path / "locations_crime_scene.csv", "w") as f:
        f.write("location\n")
        f.write("abandoned warehouse\n")
        f.write("luxury penthouse\n")
        f.write("dimly lit alley\n")
        f.write("suburban home\n")
        f.write("downtown office\n")
        f.write("parking garage\n")
    
    # Weather
    with open(output_path / "weather_ominous.csv", "w") as f:
        f.write("weather\n")
        f.write("gathering fog\n")
        f.write("steady rain\n")
        f.write("oppressive humidity\n")
        f.write("unseasonable cold\n")
        f.write("bruised storm clouds\n")
    
    # Clues - physical
    with open(output_path / "clues_physical.csv", "w") as f:
        f.write("clue\n")
        f.write("fresh scratches\n")
        f.write("muddy footprints\n")
        f.write("torn fabric\n")
        f.write("broken glass\n")
        f.write("smudged fingerprints\n")
    
    # Clues - overlooked
    with open(output_path / "clues_overlooked.csv", "w") as f:
        f.write("clue\n")
        f.write("a torn business card\n")
        f.write("an empty prescription bottle\n")
        f.write("a half-written note\n")
        f.write("unusual dust patterns\n")
        f.write("a mismatched button\n")
    
    # Suspicious details
    with open(output_path / "details_suspicious.csv", "w") as f:
        f.write("detail\n")
        f.write("unlocked door\n")
        f.write("missing photographs\n")
        f.write("recently wiped surfaces\n")
        f.write("out-of-place furniture\n")
        f.write("disconnected security camera\n")
    
    # Death positions
    with open(output_path / "positions_death.csv", "w") as f:
        f.write("position\n")
        f.write("crumpled against the far wall\n")
        f.write("sprawled across the floor\n")
        f.write("slumped over the desk\n")
        f.write("lying face-down\n")
        f.write("propped in the corner\n")
    
    # Cause of death
    with open(output_path / "death_causes.csv", "w") as f:
        f.write("cause\n")
        f.write("a single gunshot to the chest\n")
        f.write("multiple stab wounds\n")
        f.write("blunt force trauma to the head\n")
        f.write("signs of strangulation\n")
        f.write("apparent poisoning\n")
    
    # Time of day
    with open(output_path / "time_atmospheric.csv", "w") as f:
        f.write("time\n")
        f.write("dusk settled over the city\n")
        f.write("dawn broke gray and cold\n")
        f.write("midnight approached\n")
        f.write("the lunch hour ended\n")
        f.write("afternoon light faded\n")
    
    # Titles/Honorifics
    with open(output_path / "titles_formal.csv", "w") as f:
        f.write("title\n")
        f.write("Dr.\n")
        f.write("Professor\n")
        f.write("Mr.\n")
        f.write("Ms.\n")
        f.write("Detective\n")
    
    # Surfaces
    with open(output_path / "furniture_common.csv", "w") as f:
        f.write("surface\n")
        f.write("the concrete floor\n")
        f.write("the mahogany desk\n")
        f.write("the tile\n")
        f.write("the carpet\n")
        f.write("the metal table\n")
    
    print(f"Created {len(list(output_path.glob('*.csv')))} sample CSV files in '{output_dir}/'")
    return output_path


def import_csvs_for_project(csv_dir: str, project_id: int):
    """Import all CSVs from directory as world-building tables."""
    app_context = get_app_context()
    csv_path = Path(csv_dir)
    
    csv_files = list(csv_path.glob("*.csv"))
    print(f"\nImporting {len(csv_files)} CSV files for project {project_id}...\n")
    
    for csv_file in csv_files:
        # Extract table name from filename: locations_crime_scene.csv → locations.crime_scene
        table_name = csv_file.stem.replace("_", ".", 1)  # Replace first underscore with dot
        
        print(f"Importing {csv_file.name} as '{table_name}'...")
        
        import_csv_to_table(
            app_context=app_context,
            csv_path=str(csv_file),
            project_id=project_id,
            table_name=table_name,
            has_header=True,
            column_index=0
        )
    
    print(f"\nImported {len(csv_files)} tables successfully!")


def generate_scene_from_template(project_id: int, template_name: str, custom_values: dict = None):
    """Generate a scene using a template and world-building tables.
    
    Args:
        project_id: Project with world-building tables
        template_name: Name of scene template to use
        custom_values: Optional dict of custom values (not from tables)
    """
    app_context = get_app_context()
    
    # Get template
    template = app_context._session.query(SceneTemplate).filter_by(
        name=template_name
    ).first()
    
    if not template:
        raise ValueError(f"Template '{template_name}' not found")
    
    print(f"\n{'='*70}")
    print(f"GENERATING SCENE: {template.name}")
    print('='*70)
    print(f"Template: {template.scene_type}")
    print(f"Description: {template.description}\n")
    
    # Build values dict
    values = custom_values or {}
    
    # Look up table values for mapped tags
    for tag, table_ref in template.table_mappings.items():
        if tag in values:
            continue  # Already provided as custom value
            
        table = app_context._session.query(WorldBuildingTable).filter_by(
            project_id=project_id,
            table_name=table_ref
        ).first()
        
        if table:
            values[tag] = table.get_random_item()
            print(f"  {tag}: {values[tag]} (from {table_ref})")
        else:
            values[tag] = f"[{tag}]"
            print(f"  {tag}: MISSING TABLE '{table_ref}'")
    
    # Add custom values
    for tag, value in (custom_values or {}).items():
        print(f"  {tag}: {value} (custom)")
    
    # Interpolate
    result = template.interpolate(values)
    
    print(f"\n{'-'*70}")
    print("GENERATED SCENE:")
    print('-'*70)
    print(result)
    print()
    
    return result


def complete_workflow_demo(project_id: int):
    """Complete demonstration: Create CSVs → Import → Generate scenes."""
    
    print("="*70)
    print("COMPLETE WORKFLOW DEMONSTRATION")
    print("="*70)
    print()
    print("This demonstrates the full pipeline:")
    print("  1. Create sample CSV files")
    print("  2. Import them as WorldBuildingTables")
    print("  3. Generate randomized scenes from templates")
    print()
    
    # Step 1: Create sample CSVs
    print("\n" + "="*70)
    print("STEP 1: Creating Sample CSV Files")
    print("="*70)
    csv_dir = create_sample_csv_files()
    
    # Step 2: Import CSVs
    print("\n" + "="*70)
    print("STEP 2: Importing CSVs as World-Building Tables")
    print("="*70)
    import_csvs_for_project(str(csv_dir), project_id)
    
    # Step 3: Generate scenes with random elements
    print("\n" + "="*70)
    print("STEP 3: Generating Randomized Scenes")
    print("="*70)
    
    # Generate 3 variations of the same scene
    for i in range(1, 4):
        generate_scene_from_template(
            project_id=project_id,
            template_name="Crime Scene Discovery",
            custom_values={
                "detective": "Detective Morrison",
                "victim_name": "Blackwood"
            }
        )
    
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70)
    print()
    print("Next steps:")
    print("  - Add more CSV files with your own world-building elements")
    print("  - Create custom scene templates")
    print("  - Integrate with LLM for full scene generation")
    print("  - Build UI for template management")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Complete workflow demonstration: CSV import to scene generation")
        print("\nUsage:")
        print("  python workflow_demo.py <project_id>")
        print("\nExample:")
        print("  python workflow_demo.py 1")
        sys.exit(1)
    
    project_id = int(sys.argv[1])
    complete_workflow_demo(project_id)
