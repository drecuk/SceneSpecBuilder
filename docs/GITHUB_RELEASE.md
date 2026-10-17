# GitHub release guide

Repository: https://github.com/drecuk/SceneSpecBuilder

## Before the first public release

1. Select a software license and add both the license file and manifest identifier when public reuse terms are decided.
2. Run the complete validation commands from the root README.
3. Review the generated inventory, validation report, ZIP, and checksum.
4. Commit the source, create tag `v0.3.0`, and make a GitHub Release.
5. Attach the versioned ZIP and `.sha256` checksum file.

Recommended release title: `Scene Blueprint Builder 0.3.0`

Recommended release summary:

> Generates a four-panel scene blueprint for explicit visual approval, then exports matching schema-validated Blender-ready JSON. This is a skills-only plugin; Blender construction requires the separate Scene Spec Builder add-on or an existing verified Blender MCP workflow.

## Git-backed marketplace

The checked-in `.agents/plugins/marketplace.json` uses a repository-relative local source, which is the current recommended layout. Once the repository exists, users can add it with:

```bash
codex plugin marketplace add drecuk/SceneSpecBuilder
```
