# Scene Blueprint Builder plugin

This package creates a four-panel blueprint from a scene or object description, asks the user to confirm the visual and spatial plan, and then exports matching Scene Specification `1.0.0` JSON for Blender construction.

Expected completed artifacts:

- `<scene_id>_blueprint.png`
- `<scene_id>_scene_spec.json`

The plugin includes no MCP server and no authentication. Use the JSON with a separately installed Scene Spec Builder Blender add-on or an existing verified Blender MCP workflow. The poster is visual documentation; the JSON is authoritative.

Repository: https://github.com/drecuk/SceneSpecBuilder

Version: `0.3.0`
