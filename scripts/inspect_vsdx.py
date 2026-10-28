#!/usr/bin/env python3
"""Extract Visio page, shape, ShapeSheet, geometry, and media metadata."""

import argparse
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile


V = "http://schemas.microsoft.com/office/visio/2012/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"v": V, "r": R, "pr": PKG_REL}


def clean_text(element):
    if element is None:
        return ""
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def cells(parent, xpath="./v:Cell"):
    result = {}
    for cell in parent.findall(xpath, NS):
        name = cell.get("N")
        if name:
            result[name] = {
                key: value for key, value in {
                    "value": cell.get("V"),
                    "formula": cell.get("F"),
                    "unit": cell.get("U"),
                    "error": cell.get("E"),
                }.items() if value is not None
            }
    return result


def parse_shape(shape, page_name, parent_id, ancestry, output):
    shape_id = shape.get("ID")
    record = {
        "page": page_name,
        "id": shape_id,
        "parent_id": parent_id,
        "path": ancestry + [shape_id],
        "name": shape.get("Name"),
        "name_u": shape.get("NameU"),
        "type": shape.get("Type"),
        "master": shape.get("Master"),
        "master_shape": shape.get("MasterShape"),
        "line_style": shape.get("LineStyle"),
        "fill_style": shape.get("FillStyle"),
        "text_style": shape.get("TextStyle"),
        "text": clean_text(shape.find("./v:Text", NS)),
        "cells": cells(shape),
        "sections": [],
    }
    for section in shape.findall("./v:Section", NS):
        section_record = {
            "name": section.get("N"),
            "index": section.get("IX"),
            "cells": cells(section),
            "rows": [],
        }
        for row in section.findall("./v:Row", NS):
            section_record["rows"].append({
                "index": row.get("IX"),
                "name": row.get("N"),
                "type": row.get("T"),
                "cells": cells(row),
            })
        record["sections"].append(section_record)
    output.append(record)
    for child in shape.findall("./v:Shapes/v:Shape", NS):
        parse_shape(child, page_name, shape_id, record["path"], output)


def relationship_targets(archive, rel_path, source_path):
    result = {}
    if rel_path not in archive.namelist():
        return result
    root = ET.fromstring(archive.read(rel_path))
    base = posixpath.dirname(source_path)
    for relationship in root.findall("./pr:Relationship", NS):
        target = relationship.get("Target")
        if target:
            result[relationship.get("Id")] = posixpath.normpath(posixpath.join(base, target))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input .vsdx")
    parser.add_argument("output_dir", help="Directory for JSON and extracted media")
    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if input_path.suffix.lower() != ".vsdx" or not input_path.is_file():
        raise SystemExit("Input must be an existing .vsdx file")

    result = {"source": str(input_path), "pages": [], "shapes": [], "media": []}
    with zipfile.ZipFile(input_path) as archive:
        pages_path = "visio/pages/pages.xml"
        page_rels = relationship_targets(
            archive, "visio/pages/_rels/pages.xml.rels", pages_path
        )
        pages_root = ET.fromstring(archive.read(pages_path))
        page_nodes = pages_root.findall("./v:Page", NS)
        if not page_nodes:
            page_nodes = pages_root.findall(".//v:Page", NS)
        for page in page_nodes:
            rel_id = page.get("{%s}id" % R)
            if rel_id is None:
                rel_node = page.find("./v:Rel", NS)
                rel_id = rel_node.get("{%s}id" % R) if rel_node is not None else None
            target = page_rels.get(rel_id)
            page_record = {
                "id": page.get("ID"),
                "name": page.get("Name"),
                "name_u": page.get("NameU"),
                "background": page.get("Background"),
                "relationship_id": rel_id,
                "xml_part": target,
            }
            result["pages"].append(page_record)
            if target and target in archive.namelist():
                page_root = ET.fromstring(archive.read(target))
                page_name = page_record["name"] or page_record["name_u"] or page_record["id"]
                for shape in page_root.findall("./v:Shapes/v:Shape", NS):
                    parse_shape(shape, page_name, None, [], result["shapes"])

        media_dir = output_dir / "media"
        for member in archive.namelist():
            if member.startswith("visio/media/") and not member.endswith("/"):
                media_dir.mkdir(exist_ok=True)
                destination = media_dir / Path(member).name
                destination.write_bytes(archive.read(member))
                result["media"].append({
                    "package_part": member,
                    "path": str(destination),
                    "bytes": destination.stat().st_size,
                })

    result["summary"] = {
        "page_count": len(result["pages"]),
        "shape_count": len(result["shapes"]),
        "media_count": len(result["media"]),
        "shape_texts": sorted({shape["text"] for shape in result["shapes"] if shape["text"]}),
    }
    json_path = output_dir / (input_path.stem + "_visio_shapes.json")
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "json": str(json_path),
        **result["summary"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
