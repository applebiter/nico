#!/usr/bin/env python
"""Backup the PostgreSQL database with all imported data."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from nico.infrastructure.database import settings


def backup_database(output_dir: str = "db_backup") -> None:
    """Backup the PostgreSQL database to a compressed archive.
    
    Args:
        output_dir: Directory to store the backup file
    """
    # Parse database URL
    db_url = settings.get_database_url()
    # Format: postgresql://user:password@host:port/database
    
    # Extract components
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"
    database = host_db[1]
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = output_path / f"nico_db_backup_{timestamp}.sql"
    compressed_file = output_path / f"nico_db_backup_{timestamp}.tar.gz"
    
    print(f"Backing up database '{database}' from {host}:{port}")
    print(f"Output: {compressed_file}")
    
    # Set PGPASSWORD environment variable
    env = {"PGPASSWORD": password}
    
    # Dump database to SQL file
    print("\n1. Creating SQL dump...")
    dump_cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", database,
        "-f", str(backup_file),
        "--verbose",
        "--no-owner",
        "--no-privileges",
    ]
    
    result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: pg_dump failed!")
        print(result.stderr)
        sys.exit(1)
    
    print(f"✓ SQL dump created: {backup_file} ({backup_file.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Compress the SQL file
    print("\n2. Compressing backup...")
    compress_cmd = [
        "tar",
        "-czf",
        str(compressed_file),
        "-C", str(output_path),
        backup_file.name
    ]
    
    result = subprocess.run(compress_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Compression failed!")
        print(result.stderr)
        sys.exit(1)
    
    print(f"✓ Compressed: {compressed_file} ({compressed_file.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Remove uncompressed SQL file
    backup_file.unlink()
    print(f"✓ Removed uncompressed file")
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Database backed up to:")
    print(f"  {compressed_file.absolute()}")
    print(f"{'='*60}")
    
    # Show what's in the database
    print("\nDatabase contains:")
    from nico.infrastructure.database import init_db
    from nico.domain.models.world_building_table import WorldBuildingTable
    from nico.domain.models import Project, Story, Chapter, Scene, Character, Location, Event
    
    db = init_db(settings.get_database_url())
    session = db.SessionLocal()
    
    try:
        counts = {
            "Projects": session.query(Project).count(),
            "Stories": session.query(Story).count(),
            "Chapters": session.query(Chapter).count(),
            "Scenes": session.query(Scene).count(),
            "Characters": session.query(Character).count(),
            "Locations": session.query(Location).count(),
            "Events": session.query(Event).count(),
            "WorldBuildingTables": session.query(WorldBuildingTable).count(),
        }
        
        # Count total items in world-building tables
        tables = session.query(WorldBuildingTable).all()
        total_items = sum(len(t.items) for t in tables)
        
        for name, count in counts.items():
            print(f"  • {name}: {count:,}")
        
        print(f"\nWorld-Building Data:")
        print(f"  • {counts['WorldBuildingTables']} tables")
        print(f"  • {total_items:,} total data points")
        
    finally:
        session.close()


def restore_database(backup_file: str) -> None:
    """Restore the database from a backup file.
    
    Args:
        backup_file: Path to the .tar.gz backup file
    """
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"ERROR: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Extract the SQL file
    print(f"Extracting backup: {backup_path}")
    extract_cmd = ["tar", "-xzf", str(backup_path), "-C", str(backup_path.parent)]
    
    result = subprocess.run(extract_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Extraction failed!")
        print(result.stderr)
        sys.exit(1)
    
    # Find the SQL file
    sql_file = backup_path.with_suffix("").with_suffix(".sql")
    
    # Parse database URL
    db_url = settings.get_database_url()
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"
    database = host_db[1]
    
    print(f"\nRestoring to database '{database}' at {host}:{port}")
    print("WARNING: This will DROP all existing tables!")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Cancelled.")
        sql_file.unlink()
        sys.exit(0)
    
    # Set PGPASSWORD environment variable
    env = {"PGPASSWORD": password}
    
    # Restore database
    print("\nRestoring database...")
    restore_cmd = [
        "psql",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", database,
        "-f", str(sql_file),
    ]
    
    result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
    
    # Remove SQL file
    sql_file.unlink()
    
    if result.returncode != 0:
        print(f"ERROR: Restore failed!")
        print(result.stderr)
        sys.exit(1)
    
    print(f"\n✓ Database restored successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup or restore the Nico database")
    parser.add_argument(
        "action",
        choices=["backup", "restore"],
        help="Action to perform"
    )
    parser.add_argument(
        "-f", "--file",
        help="Backup file to restore from (for 'restore' action)"
    )
    parser.add_argument(
        "-o", "--output",
        default="db_backup",
        help="Output directory for backups (default: db_backup)"
    )
    
    args = parser.parse_args()
    
    if args.action == "backup":
        backup_database(args.output)
    elif args.action == "restore":
        if not args.file:
            print("ERROR: --file required for restore action")
            sys.exit(1)
        restore_database(args.file)
