# Output contract

## Normal two-stage workflow

The completed workflow produces exactly two durable deliverables:

1. `<scene_id>_blueprint.png` — the approved four-panel visual reference sheet.
2. `<scene_id>_scene_spec.json` — the matching authoritative Blender-ready specification.

Before approval, the blueprint is provisional and the assistant provides a Provisional Review Brief in the conversation. No final JSON artifact is created or claimed at that point.

## Destination and collision behavior

- Use the host's ordinary downloadable-artifact location unless the user names a destination.
- Never claim a local path the host did not return.
- Do not overwrite an existing deliverable without explicit authorization.
- On collision, add `-v2`, then increment the suffix as needed.
- Links alone are acceptable only when the host cannot expose local files; disclose that limitation.

## Required blueprint content

- One landscape poster with exactly four panels: perspective, top orthographic plan, side elevation/cross-section, and key asset/material callouts.
- Stable asset IDs shared with the review brief and JSON.
- All P1/P2 objects and significant P3 groups from the source description, with omissions disclosed.

## Required JSON content

- Valid JSON matching `scene_spec_v1.schema.json`.
- Complete scene identity, assumptions, coordinates, bounds, objects, materials, lights, camera, environment, and optional build sequence.
- Cross-references and instances without missing IDs or cycles.
- User-supplied dimensions unchanged; inferred measurements listed as assumptions.

## Success and partial failure

Success requires explicit visual approval plus valid matching JSON. A missing image, unapproved plan, invalid JSON, or undisclosed object omission is not full success. When only one deliverable can be produced, return it, name the missing deliverable, explain why, and give the smallest next step to finish.
