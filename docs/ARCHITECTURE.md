# Architecture

## Component choice

This release is intentionally skills-only.

The workflow needs reasoning, image generation, human confirmation, and JSON artifact creation. It does not need its own network service or database, and no stable public Blender MCP endpoint was supplied. Adding an invented or unverified server would make the package less accurate and less portable.

The package therefore contains:

- one portable skill, `scene-specifications-builder`;
- one portable Agent Plugins manifest;
- one Codex compatibility manifest;
- one image asset;
- five skill references, including the JSON Schema and example; and
- no `mcp.json`, `.mcp.json`, `.app.json`, hooks, server, credentials, or runtime dependencies.

## Workflow boundary

```text
story or design description
        |
        v
object and relationship inventory
        |
        v
shared provisional spatial plan
        |
        +--> four-panel blueprint --> visual inspection --> user approval
                                                     |
                                                     v
                                       validated scene_spec JSON
                                                     |
                                +--------------------+-------------------+
                                |                                        |
                                v                                        v
                     Scene Spec Builder add-on                verified Blender MCP
```

The generated image is not a metric reconstruction format. The JSON is authoritative after approval.

## MCP and authentication inventory

- MCP server count: `0`
- MCP tool count: `0`
- Authentication: none
- Commerce: none
- Local executor requirement: none for the plugin workflow

Blender or UE5 execution is downstream and outside this package. The skill must never invent endpoints, tool names, authentication, or successful construction.
