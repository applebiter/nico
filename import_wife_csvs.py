"""Smart importer for CSV files - analyzes structure and imports as world-building tables."""
import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from nico.application.context import get_app_context
from nico.domain.models import WorldBuildingTable


def analyze_csv(csv_path: Path) -> Dict:
    """Analyze a CSV file to understand its structure.
    
    Returns:
        Dict with structure info: columns, row_count, sample_rows, is_multi_column
    """
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if not rows:
                return {"valid": False, "error": "Empty file"}
            
            # Skip empty rows
            rows = [r for r in rows if any(cell.strip() for cell in r)]
            
            if not rows:
                return {"valid": False, "error": "No data rows"}
            
            # Check if first row looks like a header
            first_row = rows[0]
            has_header = any(cell and not cell.isdigit() for cell in first_row)
            
            # Count columns with data
            max_cols = max(len(row) for row in rows)
            col_data_counts = [0] * max_cols
            
            start_row = 1 if has_header else 0
            for row in rows[start_row:]:
                for i, cell in enumerate(row):
                    if i < max_cols and cell and cell.strip():
                        col_data_counts[i] += 1
            
            # Find columns with substantial data
            min_rows = len(rows[start_row:]) * 0.1  # At least 10% filled
            valid_columns = [
                i for i, count in enumerate(col_data_counts)
                if count >= min_rows
            ]
            
            return {
                "valid": True,
                "has_header": has_header,
                "header": first_row if has_header else None,
                "total_rows": len(rows),
                "data_rows": len(rows) - (1 if has_header else 0),
                "total_columns": max_cols,
                "valid_columns": valid_columns,
                "sample_rows": rows[start_row:start_row+5],
                "is_multi_column": len(valid_columns) > 1
            }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def import_single_column_csv(
    app_context,
    csv_path: Path,
    project_id: int,
    table_name: str,
    column_index: int = 0,
    has_header: bool = True,
    category: str = "random"
) -> WorldBuildingTable:
    """Import a single column from CSV as a world-building table."""
    items = []
    
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        
        if has_header:
            next(reader)  # Skip header
        
        for row in reader:
            if len(row) > column_index:
                item = row[column_index].strip()
                if item and item not in items:  # Deduplicate
                    items.append(item)
    
    if not items:
        raise ValueError(f"No items found in column {column_index}")
    
    # Create or update table
    table = app_context._session.query(WorldBuildingTable).filter_by(
        project_id=project_id,
        table_name=table_name
    ).first()
    
    if table:
        table.items = items
        table.description = f"Imported from {csv_path.name} (updated)"
    else:
        table = WorldBuildingTable(
            project_id=project_id,
            table_name=table_name,
            category=category,
            description=f"Imported from {csv_path.name}",
            items=items
        )
        app_context._session.add(table)
    
    app_context._session.commit()
    return table


def smart_import_csv(
    app_context,
    csv_path: Path,
    project_id: int,
    auto_name: bool = True
) -> List[WorldBuildingTable]:
    """Intelligently import a CSV file, creating one or more tables."""
    
    print(f"\nAnalyzing: {csv_path.name}")
    analysis = analyze_csv(csv_path)
    
    if not analysis["valid"]:
        print(f"  ❌ Skipped: {analysis['error']}")
        return []
    
    print(f"  📊 {analysis['data_rows']} rows, {analysis['total_columns']} columns")
    
    # Skip files that look like templates or documentation
    skip_keywords = ['worksheet', 'sheet1', 'template', 'outline', 'structure']
    if any(kw in csv_path.name.lower() for kw in skip_keywords):
        print(f"  ⏭️  Skipped: Looks like a template/worksheet")
        return []
    
    tables = []
    
    if analysis["is_multi_column"]:
        # Multi-column file - import each valid column separately
        print(f"  📚 Multi-column file: importing {len(analysis['valid_columns'])} columns")
        
        for col_idx in analysis['valid_columns']:
            # Build table name
            base_name = csv_path.stem.split(' - ')[0].lower().replace(' ', '_')
            
            if analysis['has_header'] and analysis['header']:
                col_name = analysis['header'][col_idx].strip().lower()
                col_name = col_name.replace(' ', '_').replace('.', '')
                table_name = f"{base_name}.{col_name}" if col_name else f"{base_name}.col{col_idx}"
            else:
                table_name = f"{base_name}.col{col_idx}"
            
            try:
                table = import_single_column_csv(
                    app_context,
                    csv_path,
                    project_id,
                    table_name,
                    column_index=col_idx,
                    has_header=analysis['has_header']
                )
                print(f"    ✓ {table_name}: {len(table.items)} items")
                tables.append(table)
            except Exception as e:
                print(f"    ✗ Column {col_idx} failed: {e}")
    else:
        # Single column file - import it
        col_idx = analysis['valid_columns'][0] if analysis['valid_columns'] else 0
        base_name = csv_path.stem.split(' - ')[-1].lower().replace(' ', '_')
        
        try:
            table = import_single_column_csv(
                app_context,
                csv_path,
                project_id,
                base_name,
                column_index=col_idx,
                has_header=analysis['has_header']
            )
            print(f"  ✓ {base_name}: {len(table.items)} items")
            tables.append(table)
        except Exception as e:
            print(f"  ✗ Import failed: {e}")
    
    return tables


def import_directory(
    app_context,
    directory: Path,
    project_id: int
) -> List[WorldBuildingTable]:
    """Import all CSV files from a directory."""
    
    csv_files = sorted(directory.glob("*.csv"))
    print(f"\n{'='*70}")
    print(f"IMPORTING {len(csv_files)} CSV FILES")
    print(f"Project ID: {project_id}")
    print(f"Directory: {directory}")
    print('='*70)
    
    all_tables = []
    
    for csv_file in csv_files:
        try:
            tables = smart_import_csv(app_context, csv_file, project_id)
            all_tables.extend(tables)
        except Exception as e:
            print(f"  ❌ Error processing {csv_file.name}: {e}")
    
    print(f"\n{'='*70}")
    print(f"IMPORT COMPLETE")
    print(f"  Total files processed: {len(csv_files)}")
    print(f"  Tables created/updated: {len(all_tables)}")
    print('='*70)
    
    return all_tables


def list_imported_tables(app_context, project_id: int):
    """List all world-building tables for a project."""
    
    tables = app_context._session.query(WorldBuildingTable).filter_by(
        project_id=project_id
    ).order_by(WorldBuildingTable.table_name).all()
    
    print(f"\n{'='*70}")
    print(f"WORLD-BUILDING TABLES FOR PROJECT {project_id}")
    print('='*70)
    
    if not tables:
        print("  No tables found.")
        return
    
    # Group by prefix
    by_prefix = {}
    for table in tables:
        prefix = table.table_name.split('.')[0]
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(table)
    
    for prefix in sorted(by_prefix.keys()):
        print(f"\n{prefix}:")
        for table in by_prefix[prefix]:
            print(f"  • {table.table_name}: {len(table.items)} items")
    
    print(f"\nTotal: {len(tables)} tables")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Smart CSV Importer for World-Building Tables")
        print("\nUsage:")
        print("  python import_wife_csvs.py import <project_id> [<csv_directory>]")
        print("  python import_wife_csvs.py list <project_id>")
        print("\nExamples:")
        print("  python import_wife_csvs.py import 1 csv_data")
        print("  python import_wife_csvs.py list 1")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "import":
        if len(sys.argv) < 3:
            print("Error: project_id required")
            sys.exit(1)
        
        project_id = int(sys.argv[2])
        csv_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("csv_data")
        
        if not csv_dir.exists():
            print(f"Error: Directory '{csv_dir}' not found")
            sys.exit(1)
        
        app_context = get_app_context()
        import_directory(app_context, csv_dir, project_id)
        list_imported_tables(app_context, project_id)
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("Error: project_id required")
            sys.exit(1)
        
        project_id = int(sys.argv[2])
        app_context = get_app_context()
        list_imported_tables(app_context, project_id)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
