#!/usr/bin/env python3
"""Validate the Scene Blueprint Builder repository, package, or release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import struct
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema
import yaml
import certifi


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_REL = Path("plugins/scene-specifications-builder-blender-mcp")
PACKAGE_ROOT = REPO_ROOT / PACKAGE_REL
MARKETPLACE_PATH = REPO_ROOT / ".agents/plugins/marketplace.json"
SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$")
FORBIDDEN_PARTS = {
    ".git",
    ".DS_Store",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".env",
}


@dataclass
class ValidationResult:
    checked_root: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require(self, condition: bool, message: str) -> None:
        if condition:
            self.checks.append(message)
        else:
            self.errors.append(message)


def load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def contained_path(root: Path, relative: str) -> Path | None:
    if not relative.startswith("./"):
        return None
    candidate = (root / relative[2:]).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", header[16:24])


def iter_package_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() or path.is_symlink())


def check_archive_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "" not in path.parts


def validate_package(
    package_root: Path, *, online_schema: bool = False, require_directory_name: bool = True
) -> ValidationResult:
    root = package_root.resolve()
    result = ValidationResult(str(root))
    result.require(root.is_dir(), "Package root exists")
    if not root.is_dir():
        return result

    files = iter_package_files(root)
    result.inventory = [path.relative_to(root).as_posix() for path in files]
    result.require(bool(files), "Package is not empty")

    for path in files:
        relative = path.relative_to(root)
        result.require(not path.is_symlink(), f"No symlink: {relative.as_posix()}")
        result.require(not any(part in FORBIDDEN_PARTS for part in relative.parts), f"No prohibited path: {relative.as_posix()}")
        result.require(path.name != ".app.json", f"No app binding file: {relative.as_posix()}")

    manifest_path = root / "plugin.json"
    compat_path = root / ".codex-plugin/plugin.json"
    skill_path = root / "skills/scene-specifications-builder/SKILL.md"
    agent_path = root / "skills/scene-specifications-builder/agents/openai.yaml"
    scene_schema_path = root / "skills/scene-specifications-builder/references/scene_spec_v1.schema.json"
    example_path = root / "skills/scene-specifications-builder/references/example_scene_spec.json"

    for required in (manifest_path, compat_path, skill_path, agent_path, scene_schema_path, example_path):
        result.require(required.is_file(), f"Required file exists: {required.relative_to(root).as_posix()}")
    if not all(path.is_file() for path in (manifest_path, compat_path, skill_path, agent_path, scene_schema_path, example_path)):
        return result

    try:
        manifest = load_json(manifest_path)
        compat = load_json(compat_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        result.errors.append(f"Manifest JSON parsing failed: {exc}")
        return result

    result.require(manifest.get("$schema") == SCHEMA_URL, "Portable schema URL is exact")
    name = manifest.get("name", "")
    version = manifest.get("version", "")
    result.require(isinstance(name, str) and len(name) <= 64 and bool(NAME.fullmatch(name)) and "--" not in name and ".." not in name, "Package name is a valid portable identifier")
    result.require(isinstance(version, str) and bool(SEMVER.fullmatch(version)), "Version is strict SemVer")
    if require_directory_name:
        result.require(root.name == name, "Package directory matches manifest name")
    result.require(compat.get("name") == name, "Compatibility name matches")
    result.require(compat.get("version") == version, "Compatibility version matches")
    result.require("$schema" not in compat, "Compatibility manifest omits portable schema")
    result.require(compat.get("skills") == "./skills/", "Compatibility skill path is portable")

    openai = manifest.get("extensions", {}).get("com.openai", {})
    interface = openai.get("interface", {})
    compat_interface = compat.get("interface", {})
    result.require(isinstance(openai, dict), "OpenAI extension is an object")
    result.require(not openai.get("apps"), "Portable manifest has no app binding")
    result.require(not compat.get("apps"), "Compatibility manifest has no app binding")
    result.require(not compat.get("extensions", {}).get("com.openai", {}).get("apps"), "Compatibility extension has no app binding")

    limits = {
        "displayName": 30,
        "shortDescription": 30,
        "longDescription": 4000,
        "developerName": 80,
    }
    for key, limit in limits.items():
        value = interface.get(key)
        result.require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit, f"{key} is nonblank and at most {limit} characters")
        result.require(compat_interface.get(key) == value, f"Compatibility {key} matches")

    result.require(isinstance(interface.get("category"), str) and bool(interface["category"].strip()), "Category is nonblank")
    result.require(isinstance(interface.get("capabilities"), list), "Capabilities is an array")
    prompts = interface.get("defaultPrompt")
    result.require(isinstance(prompts, list) and 1 <= len(prompts) <= 3, "There are one to three starter prompts")
    if isinstance(prompts, list):
        normalized: list[str] = []
        for index, prompt in enumerate(prompts, start=1):
            valid = isinstance(prompt, str) and bool(prompt.strip()) and "\n" not in prompt and len(prompt) <= 128 and "@" not in prompt
            result.require(valid, f"Starter prompt {index} is single-line, nonblank, at most 128 characters, and has no app mention")
            if isinstance(prompt, str):
                normalized.append(" ".join(prompt.split()).casefold())
        result.require(len(normalized) == len(set(normalized)), "Starter prompts are unique after whitespace normalization")
        result.require(compat_interface.get("defaultPrompt") == prompts, "Compatibility starter prompts match")

    for key in ("logo", "composerIcon"):
        value = interface.get(key)
        asset = contained_path(root, value) if isinstance(value, str) else None
        result.require(asset is not None and asset.is_file(), f"{key} resolves to a contained file")
        result.require(compat_interface.get(key) == value, f"Compatibility {key} matches")
        if asset and asset.is_file():
            try:
                width, height = png_size(asset)
                result.require(width == height, f"{key} is square")
                result.require(256 <= width <= 4096, f"{key} dimensions are within submission limits")
                result.require(asset.stat().st_size <= 5 * 1024 * 1024, f"{key} is at most 5 MiB")
            except (OSError, ValueError) as exc:
                result.errors.append(f"{key} image validation failed: {exc}")

    onboarding = openai.get("onboardingSkill")
    if onboarding is not None:
        onboarding_path = contained_path(root, onboarding) if isinstance(onboarding, str) else None
        result.require(onboarding_path == skill_path.resolve(), "Onboarding skill points to a packaged skill")

    try:
        skill_text = skill_path.read_text(encoding="utf-8")
        result.require(skill_path.stat().st_size <= 1024 * 1024, "Skill is no larger than 1 MiB")
        match = re.match(r"\A---\n(.*?)\n---\n", skill_text, flags=re.DOTALL)
        result.require(match is not None, "Skill starts with YAML frontmatter")
        if match:
            frontmatter = yaml.safe_load(match.group(1))
            result.require(frontmatter.get("name") == "scene-specifications-builder", "Skill frontmatter name matches directory")
            result.require(isinstance(frontmatter.get("description"), str) and bool(frontmatter["description"].strip()), "Skill frontmatter description is nonblank")
        for reference in (
            "references/scene_spec_v1.md",
            "references/scene_spec_v1.schema.json",
            "references/blueprint_quality.md",
            "references/output_contract.md",
            "references/conversation_starters.md",
        ):
            result.require((skill_path.parent / reference).is_file(), f"Skill reference exists: {reference}")
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        result.errors.append(f"Skill validation failed: {exc}")

    try:
        agent = yaml.safe_load(agent_path.read_text(encoding="utf-8"))
        agent_interface = agent.get("interface", {})
        result.require(agent_interface.get("display_name") == interface.get("displayName"), "Agent display name matches plugin")
        result.require(isinstance(agent_interface.get("default_prompt"), str) and bool(agent_interface["default_prompt"].strip()), "Agent default prompt is a nonblank string")
        result.require(isinstance(agent.get("policy", {}).get("allow_implicit_invocation"), bool), "Implicit invocation policy is Boolean")
        products = agent.get("policy", {}).get("products")
        result.require(isinstance(products, list) and set(products).issubset({"CHAT", "CODEX", "HERMES"}), "Agent products use supported values")
    except (OSError, UnicodeError, yaml.YAMLError, AttributeError) as exc:
        result.errors.append(f"Agent metadata validation failed: {exc}")

    try:
        scene_schema = load_json(scene_schema_path)
        example = load_json(example_path)
        jsonschema.Draft202012Validator.check_schema(scene_schema)
        jsonschema.Draft202012Validator(scene_schema).validate(example)
        result.checks.append("Example scene JSON validates against the bundled JSON Schema")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, jsonschema.SchemaError, jsonschema.ValidationError) as exc:
        result.errors.append(f"Scene specification schema validation failed: {exc}")

    if online_schema:
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(SCHEMA_URL, timeout=20, context=context) as response:
                remote_schema = json.load(response)
            jsonschema.Draft202012Validator.check_schema(remote_schema)
            jsonschema.Draft202012Validator(remote_schema).validate(manifest)
            result.checks.append("plugin.json validates against the live Agent Plugins schema")
        except Exception as exc:  # Network/schema failures must remain visible.
            result.errors.append(f"Live Agent Plugins schema validation failed: {exc}")

    for path in files:
        if path.suffix.lower() in {".json", ".md", ".yaml", ".yml"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError as exc:
                result.errors.append(f"UTF-8 validation failed for {path.relative_to(root)}: {exc}")
                continue
            result.require("/Users/" not in text and "\\Users\\" not in text, f"No machine-specific user path: {path.relative_to(root).as_posix()}")

    result.require(not (root / "mcp.json").exists(), "Skills-only package has zero MCP servers")
    result.require(not (root / ".mcp.json").exists(), "Package has no legacy MCP configuration")
    return result


def validate_marketplace(repo_root: Path, result: ValidationResult) -> None:
    path = repo_root / ".agents/plugins/marketplace.json"
    result.require(path.is_file(), "Repository marketplace file exists")
    if not path.is_file():
        return
    try:
        marketplace = load_json(path)
        result.require(isinstance(marketplace.get("name"), str) and bool(marketplace["name"].strip()), "Marketplace name is nonblank")
        result.require(isinstance(marketplace.get("interface", {}).get("displayName"), str), "Marketplace display name is present")
        plugins = marketplace.get("plugins")
        result.require(isinstance(plugins, list) and len(plugins) == 1, "Marketplace declares exactly one plugin")
        if isinstance(plugins, list) and plugins:
            entry = plugins[0]
            source = entry.get("source", {})
            source_path = source.get("path")
            resolved = contained_path(repo_root, source_path) if isinstance(source_path, str) else None
            result.require(source.get("source") == "local", "Marketplace uses a repository-local source")
            result.require(resolved == PACKAGE_ROOT.resolve(), "Marketplace source resolves to the package")
            result.require(entry.get("name") == load_json(PACKAGE_ROOT / "plugin.json").get("name"), "Marketplace plugin name matches manifest")
            policy = entry.get("policy", {})
            result.require(policy.get("installation") in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}, "Marketplace installation policy is recognized")
            result.require(isinstance(policy.get("authentication"), str) and bool(policy["authentication"]), "Marketplace authentication policy is present")
            result.require(isinstance(entry.get("category"), str) and bool(entry["category"].strip()), "Marketplace category is present")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, AttributeError) as exc:
        result.errors.append(f"Marketplace validation failed: {exc}")


def validate_archive(archive: Path, *, online_schema: bool = False) -> ValidationResult:
    archive = archive.resolve()
    result = ValidationResult(str(archive))
    result.require(archive.is_file(), "Release archive exists")
    if not archive.is_file():
        return result
    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            names = [info.filename for info in infos if not info.is_dir()]
            result.inventory = sorted(names)
            result.require(bool(names), "Release archive is not empty")
            result.require("plugin.json" in names, "Archive has plugin.json at its root")
            result.require(all(check_archive_member(name) for name in names), "Archive has no absolute or parent-traversal paths")
            for info in infos:
                mode = (info.external_attr >> 16) & 0o170000
                result.require(mode != 0o120000, f"Archive member is not a symlink: {info.filename}")
            with tempfile.TemporaryDirectory(prefix="scene-blueprint-builder-") as temp:
                destination = Path(temp)
                bundle.extractall(destination)
                package_result = validate_package(
                    destination,
                    online_schema=online_schema,
                    require_directory_name=False,
                )
                result.checks.extend(f"Extracted: {item}" for item in package_result.checks)
                result.errors.extend(f"Extracted: {item}" for item in package_result.errors)
                result.warnings.extend(f"Extracted: {item}" for item in package_result.warnings)
    except (OSError, zipfile.BadZipFile) as exc:
        result.errors.append(f"Archive validation failed: {exc}")
    return result


def render_report(result: ValidationResult, *, version: str, sha256: str | None = None) -> str:
    status = "PASS" if result.ok else "FAIL"
    checked = Path(result.checked_root)
    try:
        checked_display = checked.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        checked_display = checked.name or result.checked_root
    lines = [
        "# Validation report",
        "",
        f"- Status: **{status}**",
        f"- Version: `{version}`",
        f"- Validated target: `{checked_display}`",
        "- MCP server count: `0`",
        "- MCP tool count: `0`",
    ]
    if sha256:
        lines.append(f"- SHA-256: `{sha256}`")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {item}" for item in result.errors) if result.errors else lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {item}" for item in result.warnings) if result.warnings else lines.append("- None")
    lines.extend(["", "## Passed checks", ""])
    lines.extend(f"- {item}" for item in result.checks)
    lines.extend(["", "## Inventory", ""])
    lines.extend(f"- `{item}`" for item in result.inventory)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, help="Validate a final ZIP and its clean extraction")
    parser.add_argument("--online-schema", action="store_true", help="Also validate plugin.json against the live Agent Plugins schema")
    parser.add_argument("--report", type=Path, help="Write a Markdown validation report")
    args = parser.parse_args()

    if args.archive:
        result = validate_archive(args.archive, online_schema=args.online_schema)
    else:
        result = validate_package(PACKAGE_ROOT, online_schema=args.online_schema)
        validate_marketplace(REPO_ROOT, result)

    manifest = load_json(PACKAGE_ROOT / "plugin.json")
    sha256 = None
    if args.archive and args.archive.is_file():
        sha256 = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    report = render_report(result, version=manifest["version"], sha256=sha256)
    print(report)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
