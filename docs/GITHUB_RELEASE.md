# GitHub release guide

Repository: https://github.com/drecuk/SceneSpecBuilder

## Release checklist

1. Confirm the version in `VERSION`, both manifests, the package README, and the changelog.
2. Run the complete validation commands from the root README.
3. Review the generated inventory, validation report, ZIP, and checksum.
4. Commit the source, create the matching `v<version>` tag, and make a GitHub Release.
5. Attach the versioned ZIP and `.sha256` checksum file.

Recommended release title: `Scene Blueprint Builder 0.3.1`

Recommended release summary:

> Adds Apache-2.0 licensing, published user-input and generated-output terms, packaged legal notices, and a separate project-branding policy. Scene Blueprint Builder remains a skills-only plugin that generates an approved four-panel blueprint and matching Blender-ready JSON.

## Git-backed marketplace

The checked-in `.agents/plugins/marketplace.json` uses a repository-relative local source, which is the current recommended layout. Once the repository exists, users can add it with:

```bash
codex plugin marketplace add drecuk/SceneSpecBuilder
```
