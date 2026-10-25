#!/usr/bin/env python3
"""Apply the archived StackBox resize recipe to a locally obtained source 3MF.

Python 3.10+, standard library only. The original model is not downloaded by
this script. Its license and the creator's permissions remain applicable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import zipfile
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS = {"c": CORE}
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def bounds(vertices: list[list[float]]) -> tuple[list[float], list[float]]:
    return ([min(v[i] for v in vertices) for i in range(3)],
            [max(v[i] for v in vertices) for i in range(3)])


def write_stl(path: Path, vertices: list[list[float]], faces: list[list[int]]) -> None:
    with path.open("wb") as out:
        out.write(b"BambuLabA1-Archive / StackBox modified mesh".ljust(80, b"\0"))
        out.write(struct.pack("<I", len(faces)))
        for face in faces:
            a, b, c = [vertices[i] for i in face]
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - a[i] for i in range(3)]
            n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            length = math.sqrt(sum(x*x for x in n))
            if length <= 1e-12:
                raise ValueError("Degenerate triangle in output")
            out.write(struct.pack("<12fH", *(x/length for x in n), *a, *b, *c, 0))


def main() -> None:
    default_recipe = Path(__file__).resolve().parents[1] / "Designs/StackBox-105x147x28/Recipe.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original StackBox_V3_NoAMS_Optimal.3mf")
    parser.add_argument("--recipe", type=Path, default=default_recipe)
    parser.add_argument("--output-dir", type=Path, required=True, help="A new local directory")
    args = parser.parse_args()
    recipe = json.loads(args.recipe.read_text(encoding="utf-8"))
    source_bytes = args.source.read_bytes()
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    if source_digest != recipe["source"]["sha256"]:
        raise SystemExit("Source SHA-256 does not match the tested project. Nothing was written.")
    if args.output_dir.exists():
        raise SystemExit("Use a new output directory to avoid overwriting existing files.")

    transformed = {}
    replacements = {}
    with zipfile.ZipFile(args.source) as src:
        for part in recipe["parts"]:
            model = ET.fromstring(src.read(part["model_path"]))
            elements = model.findall(".//c:vertex", NS)
            vertices = [[float(e.get(a)) for a in "xyz"] for e in elements]
            lo, hi = bounds(vertices)
            if any(abs((hi[i]-lo[i])-part["source_extents_mm"][i]) > 1e-4 for i in range(3)):
                raise ValueError(f"Unexpected dimensions for {part['name']}")
            for point in vertices:
                for i in (0, 1):
                    centre = recipe["xy"]["straight_half_spans_mm"][i]
                    extension = recipe["xy"]["extensions_mm"][i]
                    point[i] += max(-1, min(1, point[i]/centre))*extension/2
                if part["name"] == "box":
                    low, high = recipe["z"]["stretch_interval_mm"]
                    point[2] -= max(0, min(1, (point[2]-low)/(high-low)))*recipe["z"]["shortening_mm"]
            minimum = min(p[2] for p in vertices)
            for elem, point in zip(elements, vertices):
                point[2] -= minimum
                elem.attrib.update({a: f"{v:.9f}" for a, v in zip("xyz", point)})
            faces = [[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in model.findall(".//c:triangle", NS)]
            transformed[part["name"]] = (part, vertices, faces)
            replacements[part["model_path"]] = xml_bytes(model)

        root = ET.fromstring(src.read("3D/3dmodel.model"))
        metadata_updates = {
            "Title": "StackBox para objeto 105 x 147 x 28 mm - No AMS",
            "Description": "Modified dimensions; original design Agro1223. See the BambuLabA1-Archive project for attribution, measurements and validation.",
            "ModificationDate": date.today().isoformat(),
            "Origin": "modified",
            "ProfileTitle": "105 x 147 x 28 mm + clearance | No AMS",
        }
        for element in list(root):
            if element.tag != f"{{{CORE}}}metadata":
                continue
            key = element.get("name", "")
            if key in {"Thumbnail_Middle", "Thumbnail_Small", "ProfileCover", "DesignerCover"}:
                root.remove(element)
            elif key in metadata_updates:
                element.text = metadata_updates[key]
        part_by_id = {str(p["object_id"]): p for p in recipe["parts"]}
        for item in root.findall("c:build/c:item", NS):
            position = part_by_id[item.get("objectid")]["plate_translation_mm"]
            item.set("transform", "1 0 0 0 1 0 0 0 1 " + " ".join(map(str, position)))
        replacements["3D/3dmodel.model"] = xml_bytes(root)

        settings = ET.fromstring(src.read("Metadata/model_settings.config"))
        for obj in settings.findall("object"):
            part = part_by_id[obj.get("id")]
            for meta in obj.findall(".//metadata"):
                key = meta.get("key", "")
                if key == "name":
                    meta.set("value", part["stl_filename"])
                elif key == "matrix":
                    meta.set("value", "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
                elif key.startswith("source_offset_"):
                    meta.set("value", "0")
        for plate in settings.findall("plate"):
            for meta in list(plate):
                if meta.tag == "metadata" and meta.get("key") in {"thumbnail_file", "thumbnail_no_light_file", "top_file", "pick_file"}:
                    plate.remove(meta)
        for item in settings.findall("assemble/assemble_item"):
            if item.get("volume_id") is None:
                pos = part_by_id[item.get("object_id")]["plate_translation_mm"]
                item.set("transform", "1 0 0 0 1 0 0 0 1 " + " ".join(map(str, pos)))
        replacements["Metadata/model_settings.config"] = xml_bytes(settings)

        relationships = ET.fromstring(src.read("_rels/.rels"))
        for rel in list(relationships):
            if "thumbnail" in rel.get("Type", "").lower():
                relationships.remove(rel)
        replacements["_rels/.rels"] = xml_bytes(relationships)
        args.output_dir.mkdir(parents=True)
        output = args.output_dir / recipe["output_3mf"]
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dest:
            for item in src.infolist():
                name = item.filename
                if name.startswith("Auxiliaries/") or name.startswith("Metadata/plate_") or name in {"Metadata/top_1.png", "Metadata/pick_1.png", "Metadata/slice_info.config"}:
                    continue
                dest.writestr(name, replacements.get(name, src.read(name)))
    for part, vertices, faces in transformed.values():
        write_stl(args.output_dir / part["stl_filename"], vertices, faces)
    print(output)


if __name__ == "__main__":
    main()
