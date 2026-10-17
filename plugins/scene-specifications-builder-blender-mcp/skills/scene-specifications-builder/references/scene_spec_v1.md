# Scene Specification JSON 1.0.0

Use this contract only after the user approves the Stage 1 blueprint and review brief, unless the user explicitly requests JSON-only output and skips visual review. Produce ordinary UTF-8 JSON: no comments, trailing commas, `NaN`, `Infinity`, executable code strings, or undocumented top-level fields.

The machine-readable contract is `scene_spec_v1.schema.json`. `example_scene_spec.json` is a minimal valid illustration, not a template whose content should replace the user's scene.

## Coordinate convention

- `units`: `METERS`
- `up_axis`: `Z`
- `horizontal_axes`: `["X", "Y"]`
- right-handed world coordinates
- object `position` is its geometric centre, not its bottom
- `rotation_deg` is Euler XYZ in degrees
- `dimensions` is `[width_x, depth_y, height_z]`, all strictly positive
- world bounds span X `[-width_x/2,+width_x/2]`, Y `[-depth_y/2,+depth_y/2]`, and Z `[0,height_z]`

Use a stable slug-like `scene_id`. Use unique IDs such as `OBJ_001`, `MAT_001`, and `LIGHT_001`, reusing the same IDs shown in the blueprint and review brief.

## Required top-level structure

```json
{
  "schema_version": "1.0.0",
  "scene_id": "scene_slug",
  "scene_name": "Human-readable scene name",
  "scene_description": "Design intent and narrative role",
  "assumptions": ["Every inferred measurement or content choice"],
  "coordinate_system": {
    "units": "METERS",
    "up_axis": "Z",
    "horizontal_axes": ["X", "Y"],
    "origin_description": "Where [0,0,0] is located"
  },
  "world_bounds": {"width_x": 20.0, "depth_y": 16.0, "height_z": 8.0},
  "objects": [],
  "materials": [],
  "lights": [],
  "camera": {},
  "environment": {},
  "build_sequence": []
}
```

All fields except `build_sequence` are required.

## Objects

Each object requires `id`, `name`, `type`, `position`, `rotation_deg`, `dimensions`, `material_id`, and `priority`:

```json
{
  "id": "OBJ_001",
  "name": "Display name",
  "type": "box",
  "position": [0.0, 0.0, 1.0],
  "rotation_deg": [0.0, 0.0, 0.0],
  "dimensions": [2.0, 2.0, 2.0],
  "material_id": "MAT_001",
  "priority": "P1",
  "instance_of": null,
  "parameters": {}
}
```

Supported MVP types are `box`, `cylinder`, `sphere`, `plane`, `cone`, `rock`, `tree_simple`, `terrain_grid`, `water_plane`, and `empty`. Use `empty` for unsupported complex assets and explain it with `parameters.placeholder_reason`.

Priorities are `P1` for structural/spatial essentials, `P2` for scene-defining assets, and `P3` for optional dressing. `material_id` may be `null`. `instance_of` may reference another object ID but must not form a cycle. `parameters` contains inert data only. For a repeated cluster, include a prototype plus explicit instances when exact placement matters, or one object with a documented `parameters.count` and distribution rule when the cluster is only dressing.

## Materials

Each material requires `id`, `name`, `base_color`, `roughness`, and `metallic`. Colors use `#RRGGBB` or `#RRGGBBAA`. `roughness`, `metallic`, and optional `transmission` are in `[0,1]`. Optional fields are `emission_color`, `emission_strength`, and `texture_notes`.

Do not invent materials merely to fill poster swatches.

## Lights

Supported types are `SUN`, `POINT`, `AREA`, and `SPOT`. Every light requires `id`, `name`, `type`, `position`, `color`, and nonnegative `energy`. Provide either `rotation_deg` or `target` when direction matters. `size` is optional and positive.

## Camera

The primary camera requires `position`, `target`, `resolution_x`, and `resolution_y`. Use `lens_mm: 35` and `sensor_width_mm: 36` unless the approved brief states otherwise. Optional `clip_start` and `clip_end` must be positive, with `clip_end > clip_start`. Camera position and target must differ.

## Environment

Use `world_color`, nonnegative `world_strength`, and boolean `transparent_film`. Keep atmospheric intent consistent with the approved blueprint.

## Validation beyond JSON Schema

Before saving, verify:

1. `schema_version` is exactly `1.0.0` and every required field is present.
2. All object, material, and light IDs are unique.
3. Every non-null `material_id` and `instance_of` exists.
4. The instance graph has no cycles.
5. Unsupported geometry is an explicit `empty` placeholder.
6. Numbers are finite; dimensions and bounds are positive; PBR values are in range.
7. Colors use the required hexadecimal form.
8. Camera position and target differ; `clip_end` exceeds `clip_start` when both exist.
9. Objects outside bounds are corrected or disclosed as warnings.
10. User measurements are unchanged and inferred measurements appear in `assumptions`.
11. Every P1/P2 object and significant P3 group in the approved review brief appears in JSON.
12. Blueprint labels, review IDs, JSON IDs, counts, and placement agree.

State whether validation passed and list nonfatal warnings. The blueprint remains visual documentation; this JSON is authoritative for construction.
