"""CSV import utilities for world-building tables."""
import csv
from pathlib import Path
from typing import Optional

from nico.domain.models import WorldBuildingTable
from nico.application.context import AppContext


def import_csv_to_table(
    csv_path: Path,
    project_id: int,
    table_name: str,
    app_context: AppContext,
    category: Optional[str] = None,
    description: Optional[str] = None,
    has_header: bool = True,
    column_index: int = 0,
) -> WorldBuildingTable:
    """Import a CSV file into a WorldBuildingTable.
    
    Args:
        csv_path: Path to CSV file
        project_id: Project to attach table to
        table_name: Name for the table
        app_context: Application context
        category: Optional category
        description: Optional description
        has_header: If True, skip first row
        column_index: Which column to read (0-based)
        
    Returns:
        Created WorldBuildingTable
    """
    items = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        if has_header:
            next(reader)  # Skip header
        
        for row in reader:
            if row and len(row) > column_index:
                item = row[column_index].strip()
                if item:  # Skip empty items
                    items.append(item)
    
    # Create table
    table = WorldBuildingTable(
        project_id=project_id,
        table_name=table_name,
        category=category,
        description=description,
        items=items,
    )
    
    app_context._session.add(table)
    app_context._session.commit()
    
    return table


def import_csv_with_weights(
    csv_path: Path,
    project_id: int,
    table_name: str,
    app_context: AppContext,
    category: Optional[str] = None,
    description: Optional[str] = None,
    has_header: bool = True,
    item_column: int = 0,
    weight_column: int = 1,
) -> WorldBuildingTable:
    """Import a CSV file with weights into a WorldBuildingTable.
    
    Args:
        csv_path: Path to CSV file
        project_id: Project to attach table to
        table_name: Name for the table
        app_context: Application context
        category: Optional category
        description: Optional description
        has_header: If True, skip first row
        item_column: Column index for items
        weight_column: Column index for weights
        
    Returns:
        Created WorldBuildingTable
    """
    items = []
    weights = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        if has_header:
            next(reader)  # Skip header
        
        for row in reader:
            if row and len(row) > max(item_column, weight_column):
                item = row[item_column].strip()
                if item:
                    items.append(item)
                    
                    # Try to parse weight
                    try:
                        weight = float(row[weight_column])
                        weights.append(weight)
                    except (ValueError, IndexError):
                        weights.append(1.0)  # Default weight
    
    # Create table
    table = WorldBuildingTable(
        project_id=project_id,
        table_name=table_name,
        category=category,
        description=description,
        items=items,
        weights=weights if weights else None,
    )
    
    app_context._session.add(table)
    app_context._session.commit()
    
    return table


def import_directory_of_csvs(
    directory: Path,
    project_id: int,
    app_context: AppContext,
    category: Optional[str] = None,
    has_header: bool = True,
) -> list[WorldBuildingTable]:
    """Import all CSV files in a directory as separate tables.
    
    Each CSV filename (without extension) becomes the table name.
    
    Args:
        directory: Directory containing CSV files
        project_id: Project to attach tables to
        app_context: Application context
        category: Optional category for all tables
        has_header: If True, skip first row in each file
        
    Returns:
        List of created WorldBuildingTable objects
    """
    tables = []
    
    for csv_path in directory.glob('*.csv'):
        table_name = csv_path.stem  # Filename without extension
        
        try:
            table = import_csv_to_table(
                csv_path=csv_path,
                project_id=project_id,
                table_name=table_name,
                app_context=app_context,
                category=category,
                description=f"Imported from {csv_path.name}",
                has_header=has_header,
            )
            tables.append(table)
            print(f"Imported {csv_path.name} → {table.table_name} ({len(table.items)} items)")
        except Exception as e:
            print(f"Failed to import {csv_path.name}: {e}")
    
    return tables


def export_table_to_csv(
    table: WorldBuildingTable,
    output_path: Path,
    include_weights: bool = True,
) -> None:
    """Export a WorldBuildingTable to CSV.
    
    Args:
        table: Table to export
        output_path: Output CSV path
        include_weights: If True and table has weights, include weight column
    """
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        if include_weights and table.weights:
            writer.writerow(['item', 'weight'])
            
            # Rows with weights
            for item, weight in zip(table.items, table.weights):
                writer.writerow([item, weight])
        else:
            writer.writerow(['item'])
            
            # Rows without weights
            for item in table.items:
                writer.writerow([item])
