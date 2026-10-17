# Scene Blueprint Builder

Scene Blueprint Builder is a OpenAI Agent Plugin for concept-art planning and Blender-MCP handoff. It turns a textual story, environment, interior, building, or object description into blueprints for AI agent 3D reconstructions:

1. a four-panel blueprint poster for visual review; and
2. matching Blender-ready scene JSON after the user explicitly approves the design.

The blueprint is important human-readable documentation. The confirmed JSON is the information for 3D construction.

---

## OpenAI Codex Plugin

- 📦 **[Download Scene Blueprint Builder Plugin v0.3.1](https://github.com/drecuk/SceneSpecBuilder/releases/download/v0.3.1/scene-specifications-builder-blender-mcp-0.3.1.zip)** ([release notes](https://github.com/drecuk/SceneSpecBuilder/releases/tag/v0.3.1))
- Converts a textual story, environment, interior, building, or prop description into a coordinated four-panel visual blueprint.
- Documents the perspective view, top orthographic plan, side elevation or cross-section, key objects, materials, scale, and spatial relationships for user review.
- Waits for explicit approval of the visual blueprint before exporting matching, schema-validated Scene Specification JSON.
- The approved JSON can be imported into the separate Scene Spec Builder Blender add-on or supplied to a verified Blender MCP workflow for 3D construction.
- **Requirements:** ChatGPT desktop with Codex plugin support and access to image-generation and artifact capabilities. The `codex` command is needed only for the terminal-based repository marketplace setup below. No Node.js, Python runtime, local MCP server, or authentication is required for normal plugin use.
- **SHA-256:** `4e4615a2c813016d13930a138c4217e08a09dc23c1fa5fd31a7f10220d4c59ac`

### Install from this GitHub repository

1. Make sure Codex is available in Windows PowerShell, macOS Terminal, or an Ubuntu terminal:

   ```sh
   codex --version
   ```

   If the command is unavailable, install or enable the Codex command-line tool from the ChatGPT desktop app before continuing. The plugin itself does not require Node.js.

2. Add this GitHub repository as a Codex plugin marketplace:

   ```sh
   codex plugin marketplace add drecuk/SceneSpecBuilder
   ```

3. Restart the ChatGPT desktop app so the new marketplace is loaded.

4. Open the **Plugins Directory**, select the **Scene Blueprint Tools** marketplace, open **Scene Blueprint Builder**, and select **Install**.

5. Start a new conversation and try a scene request such as:

   > Draw me a spatial layout for a modern jazz-themed cafe. I need space for a commercial espresso machine station, a cozy seating area with warm ambient lighting, and design elements that reflect a jazz club aesthetic.

6. Review the generated four-panel blueprint and its object inventory. Request any corrections to the layout, scale, objects, materials, or visual style before approving it.

7. When the blueprint is correct, explicitly confirm it, for example:

   > Approved. Generate the matching Blender-ready scene JSON.

8. Download the approved JSON and use it with the separate Scene Spec Builder Blender add-on or provide it to a verified Blender MCP workflow. The Codex plugin creates the blueprint and handoff specification; it does not create a `.blend` file on its own.

To refresh the repository package after a new release:

```sh
codex plugin marketplace upgrade scene-blueprint-tools
```

Restart the ChatGPT desktop app after upgrading if the new version does not appear immediately.

The ZIP link above is retained for release downloads, private upload, and package submission. Repository users should normally use the marketplace installation steps.

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

## Local development and direct ZIP installation

For local development, run `codex plugin marketplace add .` from the repository root to add the current checkout instead of the published GitHub marketplace.

Build the release archive:

```bash
python3 scripts/build_release.py
```

Download the ready-made ZIP and checksum from the [v0.3.1 release](https://github.com/drecuk/SceneSpecBuilder/releases/tag/v0.3.1), or use the locally built `dist/scene-specifications-builder-blender-mcp-0.3.1.zip`. The ZIP contains both portable `plugin.json` metadata and a `.codex-plugin/plugin.json` compatibility manifest.

## Upgrade and uninstall

- Marketplace install: run `codex plugin marketplace upgrade scene-blueprint-tools`, restart the app, and install the updated plugin version if prompted.
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
python3 scripts/validate_plugin.py --archive dist/scene-specifications-builder-blender-mcp-0.3.1.zip
```

The validator checks the manifests, metadata limits, conversation starters, skill frontmatter, referenced assets, icon, Scene Specification example, marketplace entry, prohibited files, symlinks, archive paths, version consistency, and optional live Agent Plugins schema validation.

## Distribution status

- GitHub repository: [drecuk/SceneSpecBuilder](https://github.com/drecuk/SceneSpecBuilder).
- Git-backed Codex marketplace: prepared and locally testable.
- Agent/Codex plugin ZIP: prepared.
- Existing private plugin update: supported by the release ZIP.
- OpenAI public directory submission: package-prepared but not submission-complete until the publisher supplies and verifies a privacy-policy URL, confirms a verified developer identity, category, and country availability, and authorizes portal upload/submission.

See [Public submission checklist](docs/PUBLIC_SUBMISSION_CHECKLIST.md), [GitHub release guide](docs/GITHUB_RELEASE.md), and [architecture notes](docs/ARCHITECTURE.md).

## License

Scene Blueprint Builder is licensed under the [Apache License 2.0](LICENSE). The installable ZIP includes the same license and declares the SPDX identifier `Apache-2.0` in both manifests.

Users retain any rights they hold in their submitted material, and the publisher does not claim ownership of generated blueprints or scene JSON, subject to applicable law and third-party platform terms. See the [Terms of Use](TERMS.md). The project name, logo, and visual identity are covered separately by the [Branding Policy](TRADEMARKS.md).
