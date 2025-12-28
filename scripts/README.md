# nico Scripts

Utility scripts for working with nico projects.

## generate_sample_data.py

Generate sample projects with dummy content for testing.

### Usage

```bash
# Generate default sample project in ~/Documents
python scripts/generate_sample_data.py

# Generate with custom name and location
python scripts/generate_sample_data.py --name "My Test Project" --path ~/Desktop

# Generate with custom author
python scripts/generate_sample_data.py --author "Your Name"
```

### Options

- `--name`: Project name (default: "Sample Project")
- `--path`: Parent directory for project (default: ~/Documents)
- `--author`: Author name (default: "Test Author")

### Sample Content

The script creates a project with two stories:

1. **The Last Lighthouse** - A short horror story with:
   - Chapter 1: The Arrival (2 scenes, ~279 words)
   - Chapter 2: Strange Tides (1 scene, ~131 words)
   - Total: ~410 words across 3 scenes

2. **Debug Story** - A minimal story for quick testing:
   - Test Chapter (2 scenes, ~14 words)

All content is stored in proper ProseMirror JSON format with word counts calculated.

### Example

```bash
$ python scripts/generate_sample_data.py --name "The Last Lighthouse" --path /tmp

Creating sample project: The Last Lighthouse
Location: /tmp
✓ Created project: The Last Lighthouse
  ✓ Created story: The Last Lighthouse
    ✓ Created chapter: Chapter 1: The Arrival
      ✓ Created scene: The Ferry Ride
        ✓ Added content (146 words)
      ✓ Created scene: The First Night
        ✓ Added content (133 words)
    ✓ Created chapter: Chapter 2: Strange Tides
      ✓ Created scene: The Morning Discovery
        ✓ Added content (131 words)
  ✓ Created story: Debug Story
    ✓ Created chapter: Test Chapter
      ✓ Created scene: Test Scene 1
        ✓ Added content (8 words)
      ✓ Created scene: Test Scene 2
        ✓ Added content (6 words)

✓ Sample project created successfully!
  Open it in nico: File → Open Project → /tmp/The Last Lighthouse
```

Then open the project in nico:
1. Launch nico
2. File → Open Project
3. Navigate to /tmp/The Last Lighthouse
4. Click scenes to view and edit content
