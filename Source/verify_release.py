"""Validate the stable RoosterWorks Station Support v1.0.5 repository layout."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "GameData" / "RoosterWorksStationSupport"
PARTS = GAME / "Parts"
MODELS = GAME / "Models"

expected_parts = {
    "RW_Hex125_Adapter",
    "RW_HexSupport_Long", "RW_HexSupport_Long_Hollow",
    "RW_HexSupport_Medium", "RW_HexSupport_Medium_Hollow",
    "RW_Octo25_Adapter",
    "RW_OctoSupport_Medium", "RW_OctoSupport_Medium_Hollow",
    "RW_OctoSupport_XL", "RW_OctoSupport_XL_Hollow",
    "RW_Octo375_Adapter",
    "RW_Octo375Support_Medium", "RW_Octo375Support_Medium_Hollow",
    "RW_Octo375Support_XL", "RW_Octo375Support_XL_Hollow",
}
expected_models = {
    "RW_Hex125_Adapter", "RW_HexSupport_Long",
    "RW_HexSupport_Long_Hollow", "RW_HexSupport_Medium",
    "RW_HexSupport_Medium_Hollow", "RW_Octo25_Adapter",
    "RW_OctoSupport_Medium", "RW_OctoSupport_Medium_Hollow",
    "RW_OctoSupport_XL", "RW_OctoSupport_XL_Hollow",
}
actual_parts = {p.stem for p in PARTS.glob("*.cfg")}
actual_models = {p.stem for p in MODELS.glob("*.mu")}
assert actual_parts == expected_parts, f"Part mismatch: missing {expected_parts - actual_parts}, extra {actual_parts - expected_parts}"
assert actual_models == expected_models, f"Model mismatch: missing {expected_models - actual_models}, extra {actual_models - expected_models}"

for name in sorted(expected_parts):
    text = (PARTS / (name + ".cfg")).read_text(encoding="utf-8")
    assert text.count("{") == text.count("}"), f"Unbalanced config: {name}"
    assert re.search(r"(?m)^\s*name\s*=\s*" + re.escape(name) + r"\s*$", text), f"Part ID mismatch: {name}"
    assert "RoosterWorksStationSupport/Models/" in text, f"Missing model path: {name}"
    assert text.count("node_stack_") >= 2, f"Missing stack nodes: {name}"
    print("PASS part", name)

for name in sorted(expected_models):
    data = (MODELS / (name + ".mu")).read_bytes()
    assert data[:8] == (76543).to_bytes(4, "little") + (5).to_bytes(4, "little"), f"Invalid MU header: {name}"
    assert len(data) > 500000, f"Unexpectedly small model: {name}"
    print("PASS model", name)

version = json.loads((GAME / "RoosterWorksStationSupport.version").read_text(encoding="utf-8"))
assert version["VERSION"] == {"MAJOR": 1, "MINOR": 0, "PATCH": 5, "BUILD": 0}
assert version["KSP_VERSION"] == {"MAJOR": 1, "MINOR": 12, "PATCH": 5}
print("PASS v1.0.5: 15 part configs, 10 models, version metadata")
