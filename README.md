# Scene Blueprint Builder

Scene Blueprint Builder is a skills-only OpenAI Agent Plugin for concept-art planning and Blender handoff. It turns a textual story, environment, interior, building, or prop description into:

1. a four-panel blueprint poster for visual review; and
2. matching Blender-ready scene JSON after the user explicitly approves the design.

The blueprint is important human-readable documentation. The confirmed JSON is the source of truth for construction.

## What it does

- Extracts the scene's objects, materials, spatial relationships, narrative anchors, and repeated elements from prose.
- Preserves every structural and scene-defining object in an auditable inventory.
- Generates perspective, top orthographic, side elevation/cross-section, and key-asset/material panels from one proposed layout.
- Stops for visual and spatial approval before creating final JSON.
- Validates the confirmed JSON against the bundled Scene Specification `1.0.0` contract.
- Hands the JSON to the separate Scene Spec Builder Blender add-on or an existing verified Blender MCP workflow.

This plugin does not bundle or claim a Blender MCP server, does not create a `.blend` file by itself, and does not infer exact measurements from image pixels.

## Repository layout

```text
.agents/plugins/marketplace.json
.github/workflows/validate.yml
plugins/scene-specifications-builder-blender-mcp/
  plugin.json
  .codex-plugin/plugin.json
  assets/scene-blueprint-builder.png
  skills/scene-specifications-builder/
scripts/build_release.py
scripts/validate_plugin.py
tests/
docs/
reports/
```

The plugin package lives under `plugins/` so the repository also acts as a repo-scoped Codex marketplace. Release ZIPs contain the plugin files at the archive root, not the repository wrapper.

## Install from this repository

From the repository root:

```bash
codex plugin marketplace add drecuk/SceneSpecBuilder
```

Restart the ChatGPT desktop app, open the Plugins Directory, choose **Scene Blueprint Tools**, and install **Scene Blueprint Builder**.

For local development, `codex plugin marketplace add .` adds the current checkout instead. If the `codex` command is unavailable, use the ChatGPT desktop app's repository marketplace flow and select `https://github.com/drecuk/SceneSpecBuilder`. The plugin itself has no authentication requirement.

## Direct ZIP installation

Build the release archive:

```bash
python3 scripts/build_release.py
```

Use `dist/scene-specifications-builder-blender-mcp-0.3.0.zip` wherever an Agent Plugin or Codex plugin ZIP is accepted. The ZIP contains both portable `plugin.json` metadata and a `.codex-plugin/plugin.json` compatibility manifest.

## Upgrade and uninstall

- Marketplace install: refresh or upgrade the marketplace, restart the app, and install the updated plugin version.
- ZIP/private install: upload the newer version to the same plugin identity rather than creating a duplicate.
- Uninstall: remove or disable the plugin from the Plugins Directory. Remove the marketplace separately only when no other plugins from that source are needed.

## Development and validation

Runtime dependencies: none bundled. The plugin relies on the host's image-generation and artifact capabilities. Blender construction requires a separately installed Blender add-on or a verified Blender MCP integration.

Development dependencies are pinned by compatible ranges in `requirements-dev.txt`:

- Python 3.10 or newer
- `jsonschema`
- `PyYAML`
- `pytest`
- `certifi` for live-schema HTTPS validation

Run:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
python3 scripts/validate_plugin.py
python3 scripts/build_release.py
python3 scripts/validate_plugin.py --archive dist/scene-specifications-builder-blender-mcp-0.3.0.zip
```

The validator checks the manifests, metadata limits, conversation starters, skill frontmatter, referenced assets, icon, Scene Specification example, marketplace entry, prohibited files, symlinks, archive paths, version consistency, and optional live Agent Plugins schema validation.

## Distribution status

- GitHub repository: [drecuk/SceneSpecBuilder](https://github.com/drecuk/SceneSpecBuilder).
- Git-backed Codex marketplace: prepared and locally testable.
- Agent/Codex plugin ZIP: prepared.
- Existing private plugin update: supported by the release ZIP.
- OpenAI public directory submission: package-prepared but not submission-complete until the publisher supplies and verifies all four public listing URLs, confirms a verified developer identity and category, chooses a license, and authorizes portal upload/submission.

See [Public submission checklist](docs/PUBLIC_SUBMISSION_CHECKLIST.md), [GitHub release guide](docs/GITHUB_RELEASE.md), and [architecture notes](docs/ARCHITECTURE.md).

## License

No public software license has been selected. Copyright remains with the author. Add a license file and manifest field only after the publisher explicitly chooses a license.
