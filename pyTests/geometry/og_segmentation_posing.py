# CLI tests for parsed 3D object segmentation
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).with_name("alicevision_object_segment.py")


@pytest.fixture
def reconstruction(tmp_path):
    """two pieces inside the crop, plus a third one outside it."""
    mesh = tmp_path / "texturedMesh.obj"
    mesh.write_text(
        "v 0 0 0\n"
        "v 1 0 0\n"
        "v 0 1 0\n"
        "v 1 1 0\n"
        "v 3 0 0\n"
        "v 4 0 0\n"
        "v 3 1 0\n"
        "v 8 0 0\n"
        "v 9 0 0\n"
        "v 8 1 0\n"
        "f 1 2 3\n"
        "f 2 4 3\n"
        "f 5/1/1 6/2/1 7/3/1\n"
        "f 8 9 10\n",
        encoding="utf-8",
    )
    return mesh


@pytest.mark.parametrize(
    ("selection", "expected_faces", "expected_x"),
    [
        ([], 3, {0.0, 1.0, 3.0, 4.0}),
        (["--largest"], 2, {0.0, 1.0}),
        (["--seed", "3", "0", "0"], 1, {3.0, 4.0}),
    ],
)
def test_extracts_expected_components(
    reconstruction, tmp_path, selection, expected_faces, expected_x
):
    output = tmp_path / "object.obj"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(reconstruction),
         "--bbox", "-1", "-1", "-1", "5", "2", "1",
         *selection, "--output", str(output)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    lines = output.read_text(encoding="utf-8").splitlines()
    vertices = [line for line in lines if line.startswith("v ")]
    faces = [line for line in lines if line.startswith("f ")]
    assert len(faces) == expected_faces
    assert {float(line.split()[1]) for line in vertices} == expected_x
    assert all(1 <= int(index) <= len(vertices)
               for face in faces for index in face.split()[1:])


def test_rejects_invalid_bbox_without_creating_output(reconstruction, tmp_path):
    output = tmp_path / "object.obj"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(reconstruction),
         "--bbox", "5", "-1", "-1", "0", "2", "1",
         "--output", str(output)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "each bbox minimum must be smaller" in result.stderr
    assert not output.exists()