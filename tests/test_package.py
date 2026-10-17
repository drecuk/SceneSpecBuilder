from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_release import build_archive
from validate_plugin import PACKAGE_ROOT, validate_archive, validate_marketplace, validate_package


def test_source_package_passes() -> None:
    result = validate_package(PACKAGE_ROOT)
    validate_marketplace(ROOT, result)
    assert result.errors == []


def test_release_archive_and_clean_extraction_pass(tmp_path: Path) -> None:
    archive, checksum, digest = build_archive(tmp_path)
    assert archive.is_file()
    assert checksum.read_text(encoding="utf-8").startswith(digest)
    result = validate_archive(archive)
    assert result.errors == []
    with zipfile.ZipFile(archive) as bundle:
        assert "plugin.json" in bundle.namelist()
        assert "LICENSE" in bundle.namelist()
        assert "TERMS.md" in bundle.namelist()
        assert "TRADEMARKS.md" in bundle.namelist()
        assert all(not name.startswith("scene-specifications-builder-blender-mcp/") for name in bundle.namelist())


def test_scene_fixture_matches_schema() -> None:
    reference = PACKAGE_ROOT / "skills/scene-specifications-builder/references"
    schema = json.loads((reference / "scene_spec_v1.schema.json").read_text(encoding="utf-8"))
    example = json.loads((reference / "example_scene_spec.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(example)


def test_requested_starter_subjects_are_present() -> None:
    manifest = json.loads((PACKAGE_ROOT / "plugin.json").read_text(encoding="utf-8"))
    prompts = " ".join(manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"]).casefold()
    assert "jazz" in prompts and "espresso" in prompts
    assert "georgian" in prompts and "emerald" in prompts
    assert "yurt" in prompts and "sheep-wool" in prompts
    assert all(len(prompt) <= 128 for prompt in manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"])


def test_plugin_is_skills_only() -> None:
    assert not (PACKAGE_ROOT / "mcp.json").exists()
    assert not (PACKAGE_ROOT / ".mcp.json").exists()
    assert not (PACKAGE_ROOT / ".app.json").exists()


def test_license_terms_and_branding_policy_are_packaged() -> None:
    manifest = json.loads((PACKAGE_ROOT / "plugin.json").read_text(encoding="utf-8"))
    compatibility = json.loads((PACKAGE_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    package_license = (PACKAGE_ROOT / "LICENSE").read_text(encoding="utf-8")
    repository_license = (ROOT / "LICENSE").read_text(encoding="utf-8")
    terms = (PACKAGE_ROOT / "TERMS.md").read_text(encoding="utf-8")

    assert manifest["license"] == "Apache-2.0"
    assert compatibility["license"] == "Apache-2.0"
    assert package_license == repository_license
    assert "Apache License" in package_license and "Version 2.0, January 2004" in package_license
    assert "does not claim ownership" in terms
    assert (PACKAGE_ROOT / "TRADEMARKS.md").is_file()
