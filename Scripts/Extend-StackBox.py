#!/usr/bin/env python3
"""Create a taller StackBox while preserving its footprint, floor and lid fit.

Python 3.10+, standard library only. The factor multiplies the box's exterior
height. Only the straight wall section is extended; the lid stays unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import io
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
BOX_PATH = "3D/Objects/object_1.model"
LID_PATH = "3D/Objects/object_2.model"
BASE_HEIGHT = 33.113126412
BASE_FLOOR = 3.2000008
BASE_CLOSED_LID_BOTTOM = 31.6000008
LOWER_FIXED_END = 6.2000008
UPPER_FIXED_START = 25.113126412


def xml_bytes(root: ET.Element) -> bytes:
    if root.tag == "{http://schemas.openxmlformats.org/package/2006/relationships}Relationships":
        ET.register_namespace("", "http://schemas.openxmlformats.org/package/2006/relationships")
        payload = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
        ET.register_namespace("", CORE)
        return payload
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True)


def read_mesh(data: bytes) -> tuple[ET.Element, list[list[float]], list[list[int]]]:
    root = ET.fromstring(data)
    vertices = [[float(e.get(a)) for a in "xyz"] for e in root.findall(".//c:vertex", NS)]
    faces = [[int(e.get(a)) for a in ("v1", "v2", "v3")] for e in root.findall(".//c:triangle", NS)]
    if not vertices or not faces:
        raise ValueError("Expected a triangular mesh")
    return root, vertices, faces


def extents(vertices: list[list[float]]) -> list[float]:
    return [max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)]


def stl_bytes(vertices: list[list[float]], faces: list[list[int]]) -> bytes:
    out = io.BytesIO()
    out.write(b"BambuLabA1-Archive / StackBox height variant".ljust(80, b"\0"))
    out.write(struct.pack("<I", len(faces)))
    for indices in faces:
        a, b, c = [vertices[i] for i in indices]
        u = [b[i]-a[i] for i in range(3)]
        v = [c[i]-a[i] for i in range(3)]
        n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        length = math.sqrt(sum(x*x for x in n))
        if length <= 1e-12:
            raise ValueError("Degenerate triangle")
        out.write(struct.pack("<12fH", *(x/length for x in n), *a, *b, *c, 0))
    return out.getvalue()


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo/"Designs/Storage/StackBox-105x147x28/Files/StackBox_105x147x28mm_Holgura_NoAMS.3mf")
    parser.add_argument("--factor", type=float, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.factor) or args.factor <= 1:
        raise SystemExit("The exterior height factor must be greater than 1.")
    if args.output_dir.exists():
        raise SystemExit("Choose a new output directory to avoid overwriting files.")
    tag = f"{args.factor:g}x"
    filename = f"StackBox_Height{tag}_NoAMS.3mf"
    box_filename = f"StackBox_Caja_Height{tag}.stl"
    lid_filename = "StackBox_Tapa_Compatible.stl"
    replacements = {}
    source_bytes = args.source.read_bytes()
    with zipfile.ZipFile(io.BytesIO(source_bytes)) as src:
        model, vertices, faces = read_mesh(src.read(BOX_PATH))
        lid_model, lid_vertices, lid_faces = read_mesh(src.read(LID_PATH))
        measured = extents(vertices)
        expected = [156.3200062, 114.3200062, BASE_HEIGHT]
        if any(abs(a-b) > 1e-5 for a, b in zip(measured, expected)):
            raise SystemExit("The source is not the archived base StackBox geometry.")
        if any(abs(a-b) > 1e-5 for a, b in zip(extents(lid_vertices), [*expected[:2], 8.0])):
            raise SystemExit("Unexpected lid dimensions.")
        new_height = measured[2]*args.factor
        config = json.loads(src.read("Metadata/project_settings.config"))
        printer_height = float(config.get("printable_height", "256"))
        if new_height > printer_height:
            raise SystemExit(f"The result ({new_height:.2f} mm) exceeds the configured printer height ({printer_height:g} mm).")
        extra = new_height-measured[2]
        for element, point in zip(model.findall(".//c:vertex", NS), vertices):
            blend = max(0.0, min(1.0, (point[2]-LOWER_FIXED_END)/(UPPER_FIXED_START-LOWER_FIXED_END)))
            point[2] += blend*extra
            element.set("z", f"{point[2]:.9f}")
        replacements[BOX_PATH] = xml_bytes(model)

        project = ET.fromstring(src.read("3D/3dmodel.model"))
        metadata = {e.get("name"): e for e in project.findall("c:metadata", NS)}
        updates = {
            "Title": f"StackBox - Height {tag} - No AMS",
            "Description": f"Height-only derivative of the 105 x 147 x 28 mm StackBox adaptation. Original design: Agro1223. Exterior height: {new_height:.6f} mm. Same footprint and lid; floor and rim profiles preserved. Exterior height multiplied by {args.factor:g}.",
            "ModificationDate": date.today().isoformat(),
            "Origin": "modified",
            "ProfileTitle": f"StackBox Height {tag} | Bambu A1 | No AMS",
            "ProfileDescription": "Height-only variant. Original archived print settings retained. Re-slice before printing.",
        }
        for key, value in updates.items():
            if key in metadata:
                metadata[key].text = value
            else:
                ET.SubElement(project, f"{{{CORE}}}metadata", {"name": key}).text = value
        for element in list(project):
            if element.tag == f"{{{CORE}}}metadata" and element.get("name") in {"Thumbnail_Middle", "Thumbnail_Small", "DesignerCover", "ProfileCover"}:
                project.remove(element)
        replacements["3D/3dmodel.model"] = xml_bytes(project)

        settings = ET.fromstring(src.read("Metadata/model_settings.config"))
        names = {"2": box_filename, "4": lid_filename}
        for obj in settings.findall("object"):
            for meta in obj.findall(".//metadata"):
                if meta.get("key") == "name":
                    meta.set("value", names[obj.get("id")])
        for plate in settings.findall("plate"):
            for meta in list(plate):
                if meta.tag == "metadata" and meta.get("key") in {"thumbnail_file", "thumbnail_no_light_file", "top_file", "pick_file"}:
                    plate.remove(meta)
        replacements["Metadata/model_settings.config"] = xml_bytes(settings)
        relationships = ET.fromstring(src.read("_rels/.rels"))
        for rel in list(relationships):
            if "thumbnail" in rel.get("Type", "").lower():
                relationships.remove(rel)
        replacements["_rels/.rels"] = xml_bytes(relationships)
        if "Metadata/plate_1.json" in src.namelist():
            plate = json.loads(src.read("Metadata/plate_1.json"))
            for entry, name in zip(plate.get("bbox_objects", []), [box_filename, lid_filename]):
                entry["name"] = name
            plate.pop("first_layer_time", None)
            replacements["Metadata/plate_1.json"] = json.dumps(plate).encode()

        args.output_dir.mkdir(parents=True)
        with zipfile.ZipFile(args.output_dir/filename, "w", zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                if ".gcode" in item.filename or item.filename == "Metadata/slice_info.config" or item.filename.startswith("Auxiliaries/") or item.filename.lower().endswith((".png", ".webp")):
                    continue
                dst.writestr(item.filename, replacements.get(item.filename, src.read(item.filename)))

    (args.output_dir/box_filename).write_bytes(stl_bytes(vertices, faces))
    (args.output_dir/lid_filename).write_bytes(stl_bytes(lid_vertices, lid_faces))
    recipe = {
        "name": f"StackBox-Height{tag}",
        "units": "millimeter",
        "axes": "X length, Y width, Z height",
        "source_project": "Designs/Storage/StackBox-105x147x28/Files/StackBox_105x147x28mm_Holgura_NoAMS.3mf",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "exterior_height_factor": args.factor,
        "base_exterior_height_mm": measured[2],
        "additional_wall_height_mm": extra,
        "exterior_box_xyz_mm": extents(vertices),
        "exterior_lid_xyz_mm": extents(lid_vertices),
        "usable_rectangular_xyz_mm": [147.4, 105.4, BASE_CLOSED_LID_BOTTOM+extra-BASE_FLOOR],
        "floor_height_mm": BASE_FLOOR,
        "closed_lid_bottom_mm": BASE_CLOSED_LID_BOTTOM+extra,
        "wall_stretch_interval_mm": [LOWER_FIXED_END, UPPER_FIXED_START],
        "printable_height_mm": printer_height,
        "lid_compatible_with_base": True,
        "output_3mf": filename,
        "output_stl_box": box_filename,
        "output_stl_lid": lid_filename,
    }
    (args.output_dir/"Derivation.json").write_text(json.dumps(recipe, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(recipe, indent=2))


if __name__ == "__main__":
    main()
