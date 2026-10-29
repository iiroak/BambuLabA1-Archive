#!/usr/bin/env python3
"""Prepare separate A1 projects for the two tall containers and their two lids.

Python 3.10+, standard library only. This creates editable projects; slicing
must be performed in Bambu Studio. The published plates also include sliced
files for the configured A1 / 0.4 mm / PLA setup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
import zipfile
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"c": CORE}
ET.register_namespace("p", PROD)
CENTRES = [(66.8399969, 128.0), (189.1600031, 128.0)]
MESH_PATHS = ["3D/Objects/object_1.model", "3D/Objects/object_2.model"]


def xml_bytes(root):
    namespace = REL if root.tag == f"{{{REL}}}Relationships" else CORE
    ET.register_namespace("", namespace)
    value = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    ET.register_namespace("", CORE)
    return value


def transform(slot):
    x, y = CENTRES[slot]
    return f"0 1 0 -1 0 0 0 0 1 {x:.9f} {y:.9f} 0"


def mesh_bounds(root):
    vertices = [[float(e.get(a)) for a in "xyz"] for e in root.findall(".//c:vertex", NS)]
    if not vertices:
        raise ValueError("Expected a mesh")
    return ([min(v[i] for v in vertices) for i in range(3)],
            [max(v[i] for v in vertices) for i in range(3)])


def make_plate(base_path, selections, output_path, title, description):
    replacements = {}
    items = []
    with zipfile.ZipFile(base_path) as base:
        project = ET.fromstring(base.read("3D/3dmodel.model"))
        settings = ET.fromstring(base.read("Metadata/model_settings.config"))
        plate_data = json.loads(base.read("Metadata/plate_1.json"))
        for slot, selection in enumerate(selections):
            with zipfile.ZipFile(selection["source"]) as src:
                root = ET.fromstring(src.read(selection["mesh"]))
            mesh_object = root.find("c:resources/c:object", NS)
            mesh_id, object_id = (1, 2) if slot == 0 else (3, 4)
            mesh_object.set("id", str(mesh_id))
            mesh_object.set(f"{{{PROD}}}UUID", str(uuid.uuid4()))
            replacements[MESH_PATHS[slot]] = xml_bytes(root)
            lo, hi = mesh_bounds(root)
            x, y = CENTRES[slot]
            # +90 degrees around Z: new X=-old Y, new Y=old X.
            plate_lo = [x-hi[1], y+lo[0], lo[2]]
            plate_hi = [x-lo[1], y+hi[0], hi[2]]
            if any(v < 0 for v in plate_lo) or any(v > 256 for v in plate_hi):
                raise ValueError("Part lies outside the A1 print volume")
            count = len(root.findall(".//c:triangle", NS))
            parent = project.find(f"c:resources/c:object[@id='{object_id}']", NS)
            parent.set(f"{{{PROD}}}UUID", str(uuid.uuid4()))
            component = parent.find("c:components/c:component", NS)
            component.set(f"{{{PROD}}}UUID", str(uuid.uuid4()))
            component.set("objectid", str(mesh_id))
            component.set(f"{{{PROD}}}path", "/"+MESH_PATHS[slot])
            build_item = project.find(f"c:build/c:item[@objectid='{object_id}']", NS)
            build_item.set("transform", transform(slot))
            build_item.set(f"{{{PROD}}}UUID", str(uuid.uuid4()))
            obj = settings.find(f"object[@id='{object_id}']")
            part = obj.find("part")
            part.set("id", str(mesh_id)); part.set("uuid", str(uuid.uuid4()))
            for element in obj.findall(".//metadata"):
                key = element.get("key", "")
                if key == "name": element.set("value", selection["name"])
                if key == "extruder": element.set("value", "1")
                if key == "matrix": element.set("value", "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
                if key.startswith("source_offset_"): element.set("value", "0")
                if "face_count" in element.attrib: element.set("face_count", str(count))
            for element in obj.findall(".//mesh_stat"): element.set("face_count", str(count))
            for element in settings.findall(f"assemble/assemble_item[@object_id='{object_id}']"):
                if element.get("volume_id") is None: element.set("transform", transform(slot))
            entry = plate_data["bbox_objects"][slot]
            entry["name"] = selection["name"]
            entry["bbox"] = [*plate_lo[:2], *plate_hi[:2]]
            items.append({
                "name": selection["name"], "source_sha256": hashlib.sha256(selection["source"].read_bytes()).hexdigest(),
                "mesh_id": mesh_id, "object_id": object_id,
                "mesh_path": MESH_PATHS[slot], "plate_bbox_xyz_mm": [plate_lo, plate_hi],
                "rotation_z_degrees": 90, "translation_mm": [x,y,0], "triangles": count,
            })
        for element in list(project):
            if element.tag == f"{{{CORE}}}metadata" and element.get("name") in {"Thumbnail_Middle", "Thumbnail_Small", "DesignerCover", "ProfileCover"}:
                project.remove(element)
        updates = {"Title": title, "Description": description, "ProfileTitle": title,
                   "ProfileDescription": "A1, 0.4 mm nozzle, PLA Basic, 0.28 mm layers, one filament, by-layer printing.",
                   "ModificationDate": date.today().isoformat(), "Origin": "modified"}
        for element in project.findall("c:metadata", NS):
            if element.get("name") in updates: element.text = updates[element.get("name")]
        project.find("c:build", NS).set(f"{{{PROD}}}UUID", str(uuid.uuid4()))
        replacements["3D/3dmodel.model"] = xml_bytes(project)
        for plate in settings.findall("plate"):
            for element in list(plate):
                if element.tag == "metadata" and element.get("key") in {"thumbnail_file", "thumbnail_no_light_file", "top_file", "pick_file"}: plate.remove(element)
            for element in plate.findall("metadata"):
                if element.get("key") == "plater_name": element.set("value", title)
        replacements["Metadata/model_settings.config"] = xml_bytes(settings)
        rectangles = [entry["bbox"] for entry in plate_data["bbox_objects"]]
        plate_data["bbox_all"] = [min(b[0] for b in rectangles), min(b[1] for b in rectangles), max(b[2] for b in rectangles), max(b[3] for b in rectangles)]
        plate_data.pop("first_layer_time", None)
        replacements["Metadata/plate_1.json"] = json.dumps(plate_data).encode()
        config = json.loads(base.read("Metadata/project_settings.config"))
        if config["printer_model"] != "Bambu Lab A1" or config["nozzle_diameter"] != ["0.4"]:
            raise ValueError("Expected the archived A1 / 0.4 mm configuration")
        config["print_sequence"] = "by layer"
        config["enable_prime_tower"] = "0"
        replacements["Metadata/project_settings.config"] = json.dumps(config, indent=2).encode()
        rels = ET.fromstring(base.read("_rels/.rels"))
        for rel in list(rels):
            if "thumbnail" in rel.get("Type", "").lower(): rels.remove(rel)
        replacements["_rels/.rels"] = xml_bytes(rels)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as dst:
            for info in base.infolist():
                name = info.filename
                if name.startswith("Auxiliaries/") or name.lower().endswith((".png", ".webp")) or ".gcode" in name or name == "Metadata/slice_info.config": continue
                dst.writestr(name, replacements.get(name, base.read(name)))
    return {"project": output_path.name, "title": title, "items": items, "bed_mm": [256,256],
            "printable_height_mm": 256, "gap_between_parts_mm": 8.0, "print_sequence": "by layer",
            "printer": "Bambu Lab A1", "nozzle_mm": .4, "filament": "Bambu PLA Basic", "filaments": 1}


def main():
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.output_dir.exists(): raise SystemExit("Choose a new output directory.")
    source3 = repo/"Designs/Storage/StackBox-Height3x/Files/StackBox_Height3x_NoAMS.3mf"
    source6 = repo/"Designs/Storage/StackBox-Height6x/Files/StackBox_Height6x_NoAMS.3mf"
    if not source3.is_file() or not source6.is_file(): raise SystemExit("Both archived height variants are required.")
    projects = args.output_dir/"Projects"; projects.mkdir(parents=True)
    containers = make_plate(source3, [
        {"source":source3,"mesh":"3D/Objects/object_1.model","name":"StackBox_Recipiente_3x.stl"},
        {"source":source6,"mesh":"3D/Objects/object_1.model","name":"StackBox_Recipiente_6x.stl"},
    ], projects/"StackBox_A1_2_Recipientes.3mf", "StackBox - 2 recipientes - 3x y 6x - A1", "Two containers, exterior heights 99.339379 and 198.678758 mm. Original design Agro1223. Separate lids are in the two-lids project.")
    lids = make_plate(source3, [
        {"source":source3,"mesh":"3D/Objects/object_2.model","name":"StackBox_Tapa_1.stl"},
        {"source":source3,"mesh":"3D/Objects/object_2.model","name":"StackBox_Tapa_2.stl"},
    ], projects/"StackBox_A1_2_Tapas.3mf", "StackBox - 2 tapas compatibles - A1", "Two identical lids, compatible with the base StackBox and both height variants. Original design Agro1223.")
    layout = {"units":"millimeter", "plates":{"containers":containers,"lids":lids}}
    (args.output_dir/"Layout.json").write_text(json.dumps(layout,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(layout,indent=2))


if __name__ == "__main__": main()
