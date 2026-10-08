# v2 -> updated and installed on this machine for git management 09/26
# - sid

#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


def read_obj(path: Path):
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    with path.open("r", encoding="utf-8", errors="replace") as source:
        for line_number, line in enumerate(source, 1):
            fields = line.split()
            if not fields or fields[0] == "#":
                continue
            if fields[0] == "v" and len(fields) >= 4:
                vertices.append(tuple(map(float, fields[1:4])))
            elif fields[0] == "f" and len(fields) >= 4:
                face = []
                for token in fields[1:]:
                    raw_index = int(token.split("/")[0])
                    index = raw_index - 1 if raw_index > 0 else len(vertices) + raw_index
                    if not 0 <= index < len(vertices):
                        raise ValueError(f"Invalid vertex index on line {line_number}")
                    face.append(index)
                faces.append(tuple(face))
    if not vertices or not faces:
        raise ValueError("Input OBJ must contain vertices and faces")
    return vertices, faces


def inside_box(vertex, box):
    xmin, ymin, zmin, xmax, ymax, zmax = box
    x, y, z = vertex
    return xmin <= x <= xmax and ymin <= y <= ymax and zmin <= z <= zmax


def connected_components(faces, selected):
    """CRAZY optmization -> group faces = translatable vertices!!!"""
    by_vertex = defaultdict(list)
    for face_index in selected:
        for vertex_index in faces[face_index]:
            by_vertex[vertex_index].append(face_index)

    unseen = set(selected)
    components = []
    while unseen:
        start = unseen.pop()
        stack = [start]
        component = [start]
        while stack:
            face_index = stack.pop()
            for vertex_index in faces[face_index]:
                for neighbor in by_vertex[vertex_index]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        component.append(neighbor)
                        stack.append(neighbor)
        components.append(component)
    return components


def distance_squared(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def write_obj(path, vertices, faces, selected):
    used = sorted({vertex for index in selected for vertex in faces[index]})
    remap = {original: new for new, original in enumerate(used, 1)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        output.write("# Geometry extracted from an AliceVision/Meshroom OBJ\n")
        for original in used:
            x, y, z = vertices[original]
            output.write(f"v {x:.9g} {y:.9g} {z:.9g}\n")
        for index in sorted(selected):
            output.write("f " + " ".join(str(remap[v]) for v in faces[index]) + "\n")
    return len(used)