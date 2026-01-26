# ComfyUI Workflow Presets

This directory contains ComfyUI workflow JSON files used by Nico for image generation.

## Managing Workflows

You can manage these workflows through the GUI:
1. Open Nico application
2. Go to **Tools → ComfyUI Workflows...**
3. Use the Workflow Manager to:
   - Import new workflows (drag-and-drop or browse)
   - Preview workflow JSON
   - Delete workflows
   - Export workflows

## Default Workflows

### image_z_image_turbo.json
Standard fast image generation using z-image-turbo model.
- **Use case:** Quick character portraits, locations, scenes
- **Speed:** Fast (~2-4 seconds)
- **Quality:** Good for story illustrations

### sdxl_revision_text_prompts.json
SDXL Revision workflow for style transfer with two reference images.
- **Use case:** Maintaining visual continuity across generations
- **Features:** unCLIP conditioning with CLIP Vision encoding
- **Parameters:** 2 reference images + text prompt + style strength (0.6-0.95)
- **Recommended resolutions:** Use SDXL-trained dimensions for best quality:
  - 1024 × 1024 (square)
  - 1152 × 896 / 896 × 1152 (portrait/landscape)
  - 1216 × 832 / 832 × 1216 (portrait/landscape)
  - 1344 × 768 / 768 × 1344 (wide/tall)
  - 1536 × 640 / 640 × 1536 (ultrawide/ultratall)

## SDXL Resolution Guidelines

SDXL models are trained on specific resolutions for optimal quality. When generating images, use these trained dimensions:

| Aspect Ratio | Resolution | Best For |
|--------------|------------|----------|
| 1:1 (Square) | 1024 × 1024 | Portraits, profile images |
| 4:5 (Portrait) | 832 × 1216 | Character full body |
| 7:9 (Portrait) | 896 × 1152 | Tall portraits |
| 5:4 (Landscape) | 1216 × 832 | Scenes, landscapes |
| 9:7 (Landscape) | 1152 × 896 | Wide scenes |
| 7:4 (Wide) | 1344 × 768 | Cinematic wide |
| 12:5 (Wide) | 1536 × 640 | Ultrawide panorama |
| 4:7 (Tall) | 768 × 1344 | Tall narrow scenes |
| 5:12 (Tall) | 640 × 1536 | Vertical panorama |

**Why use these specific resolutions?**
- Better image quality (model was trained on these)
- More coherent compositions
- Fewer artifacts and distortions
- Optimal performance

The GUI presets automatically use these trained resolutions.

## Adding Custom Workflows

### Method 1: GUI (Recommended)
1. Open **Tools → ComfyUI Workflows...**
2. Drag-and-drop your JSON file onto the drop zone
3. Or click **Browse** to select a file

### Method 2: Manual
1. Save your workflow from ComfyUI (API format)
2. Copy the JSON file to this directory
3. Restart Nico or click **Refresh** in Workflow Manager

## Workflow Requirements

Valid workflow files must:
- Be valid JSON format
- Follow ComfyUI API workflow structure
- Have unique node IDs
- Include all required node connections

## Using Workflows in Code

```python
from nico.presentation.widgets.workflow_manager import get_workflow_path

# Get path to a workflow
workflow_path = get_workflow_path("image_z_image_turbo.json")

# Or use directly in services
from nico.infrastructure.comfyui_service import ComfyUIService
comfyui = ComfyUIService()  # Automatically uses image_z_image_turbo.json

from nico.infrastructure.style_transfer_workflow import StyleTransferWorkflow
style = StyleTransferWorkflow()  # Automatically uses sdxl_revision_text_prompts.json
```

## Troubleshooting

### "Workflow not found" error
- Check that the JSON file exists in this directory
- Verify the filename matches exactly (case-sensitive)
- Use Workflow Manager to verify it's listed

### "Invalid workflow" when importing
- Ensure it's exported from ComfyUI in API format (not PNG)
- Validate JSON syntax with a JSON validator
- Check that it's a dictionary/object, not an array

### Workflow doesn't work in ComfyUI
- Ensure all custom nodes are installed
- Check node IDs don't conflict
- Verify all required inputs are connected
