"""Validate the exact reviewed report package before GitHub Pages publication."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
manifest = json.loads((SITE / "data-app-build.json").read_text())
assert manifest["kind"] == "source-single-file-v1"
for kind in ("html", "snapshot"):
    entry = manifest[kind]
    path = SITE / entry["path"]
    assert path.parent == SITE and path.is_file(), f"Missing package file: {kind}"
    data = path.read_bytes()
    assert len(data) == entry["bytes"], f"File size changed: {kind}"
    assert sha256(data).hexdigest() == entry["sha256"], f"Checksum mismatch: {kind}"

snapshot = json.loads((SITE / manifest["snapshot"]["path"]).read_text())
assert snapshot["title"] == "Email Campaign Analysis"
assert snapshot["buildStatus"] == "complete"
assert sum(row["customers"] for row in snapshot["queries"]["campaign_summary"]["rows"]) == 64000
assert sha256((ROOT / "web/src/data.json").read_bytes()).hexdigest() == manifest["sourceSnapshotSha256"], "Rebuild site/ after source-data changes"
html = (SITE / "index.html").read_text()
assert f'name="data-app-snapshot-sha256" content="{manifest["sourceSnapshotSha256"]}"' in html
assert manifest["snapshot"]["sha256"] == manifest["sourceSnapshotSha256"]
assert sha256((ROOT / "web/protected-runtime.json").read_bytes()).hexdigest() == manifest["protectedRuntimeSha256"]
assert '<meta name="data-app-local-thread"' not in html
assert '<meta name="data-app-local-reference"' not in html
print("Verified visitor report package, source integrity, aggregate snapshot and 64,000-customer denominator.")
