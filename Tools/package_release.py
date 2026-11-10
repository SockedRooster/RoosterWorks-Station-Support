"""Verify release hashes and package the install and repository-root source."""
from pathlib import Path
import hashlib, json, zipfile

root = Path(__file__).resolve().parents[1]
meta = json.loads((root / "RELEASE_METADATA.json").read_text())
stem = meta["repository"].split("/")[-1] + "-v" + meta["version"]
gd = root / "GameData"
payload = sorted(p for p in gd.rglob("*") if p.is_file())
hashes = {p.relative_to(gd).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in payload}
assert hashes == json.loads((root / "Reports/ACCEPTED_RUNTIME_SHA256.json").read_text())
archived_list = root / "Docs/ARCHIVED_PREVIEWS.txt"
archived_previews = set(archived_list.read_text(encoding="utf-8").splitlines()) if archived_list.exists() else set()
source = sorted(p for p in root.rglob("*") if p.is_file() and not
                set(p.relative_to(root).parts).intersection({".git", ".build-deps", "__pycache__", "dist"})
                and p.relative_to(root).as_posix() not in archived_previews
                and p.name != "CHECKSUMS-SHA256.txt" and p.suffix not in {".pyc", ".zip"})
manifest = root / "CHECKSUMS-SHA256.txt"
manifest.write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " +
                            p.relative_to(root).as_posix() + "\n" for p in source), encoding="utf-8")
for suffix, files in [("", payload), ("-GitHub-Source", source + [manifest])]:
    path = root.parent / (stem + suffix + ".zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for file in files:
            archive.write(file, file.relative_to(root).as_posix())
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist()) == len(files)
        for file in files:
            assert archive.read(file.relative_to(root).as_posix()) == file.read_bytes()
