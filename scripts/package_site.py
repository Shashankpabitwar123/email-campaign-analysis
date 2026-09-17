"""Package the visitor-mode source build and its reviewed aggregate snapshot."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
html = (ROOT / "web/dist/index.html").read_bytes()
snapshot = (ROOT / "web/src/data.json").read_bytes()
snapshot_hash = sha256(snapshot).hexdigest()
assert json.loads(snapshot)["buildStatus"] == "complete"
assert f'name="data-app-snapshot-sha256" content="{snapshot_hash}"'.encode() in html
assert b'<meta name="data-app-local-thread"' not in html
assert b'<meta name="data-app-local-reference"' not in html
SITE.mkdir(exist_ok=True)
snapshot_name = f"snapshot.{snapshot_hash}.json"
for path in SITE.glob("snapshot.*.json"):
    if path.name != snapshot_name:
        path.unlink()
(SITE / "index.html").write_bytes(html)
(SITE / snapshot_name).write_bytes(snapshot)
manifest = {
    "version": 1,
    "kind": "source-single-file-v1",
    "html": {"path": "index.html", "sha256": sha256(html).hexdigest(), "bytes": len(html)},
    "snapshot": {"path": snapshot_name, "sha256": snapshot_hash, "bytes": len(snapshot)},
    "sourceSnapshotSha256": snapshot_hash,
    "protectedRuntimeSha256": sha256((ROOT / "web/protected-runtime.json").read_bytes()).hexdigest(),
}
(SITE / "data-app-build.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Packaged the visitor-mode source build with unchanged reviewed aggregate data.")
