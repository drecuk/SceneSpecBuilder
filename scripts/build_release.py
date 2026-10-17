#!/usr/bin/env python3
"""Build a deterministic plugin ZIP, checksum, inventory, and validation report."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_plugin import PACKAGE_ROOT, REPO_ROOT, render_report, validate_archive, validate_marketplace, validate_package


def build_archive(output_dir: Path | None = None) -> tuple[Path, Path, str]:
    manifest = json.loads((PACKAGE_ROOT / "plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    name = manifest["name"]
    destination = (output_dir or REPO_ROOT / "dist").resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{name}-{version}.zip"
    checksum_path = destination / f"{name}-{version}.zip.sha256"

    source_result = validate_package(PACKAGE_ROOT)
    validate_marketplace(REPO_ROOT, source_result)
    if not source_result.ok:
        raise RuntimeError("Source validation failed:\n" + "\n".join(source_result.errors))

    files = sorted(path for path in PACKAGE_ROOT.rglob("*") if path.is_file())
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in files:
            relative = path.relative_to(PACKAGE_ROOT).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 10, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum_path.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")

    archive_result = validate_archive(archive)
    if not archive_result.ok:
        raise RuntimeError("Clean-extraction validation failed:\n" + "\n".join(archive_result.errors))

    if output_dir is None:
        reports = REPO_ROOT / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "package-inventory.txt").write_text("\n".join(archive_result.inventory) + "\n", encoding="utf-8")
        (reports / "validation-report.md").write_text(
            render_report(archive_result, version=version, sha256=digest), encoding="utf-8"
        )
    return archive, checksum_path, digest


def main() -> int:
    archive, checksum, digest = build_archive()
    print(f"Built: {archive}")
    print(f"Checksum: {checksum}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
