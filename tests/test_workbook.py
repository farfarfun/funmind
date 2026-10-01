import zipfile

import pytest

import funmind.xmind as xmind
from funmind.xmind.core.markerref import MarkerId
from funmind.xmind.core.loader import WorkbookLoader
from funmind.xmind.exceptions import InvalidXMindFileError


def test_load_missing_file_creates_empty_workbook(tmp_path):
    workbook = xmind.load(str(tmp_path / "missing.xmind"))
    assert workbook.get_primary_sheet() is not None


def test_load_rejects_non_xmind_extension(tmp_path):
    with pytest.raises(InvalidXMindFileError):
        WorkbookLoader(str(tmp_path / "bad.txt"))


def test_save_rejects_non_xmind_extension_with_path_context(tmp_path):
    workbook = xmind.load(str(tmp_path / "source.xmind"))
    invalid_path = tmp_path / "bad.txt"

    with pytest.raises(InvalidXMindFileError) as exc_info:
        xmind.save(workbook, path=str(invalid_path))

    assert str(invalid_path) in str(exc_info.value)
    assert ".xmind" in str(exc_info.value)


def test_load_corrupted_file_falls_back_to_empty_workbook(tmp_path):
    path = tmp_path / "corrupt.xmind"
    path.write_text("not a zip file")

    loader = WorkbookLoader(str(path))
    assert loader._content_stream is None


def test_save_then_load_round_trip(tmp_path):
    path = str(tmp_path / "demo.xmind")

    workbook = xmind.load(path)
    sheet = workbook.get_primary_sheet()
    sheet.set_title("first sheet")

    root_topic = sheet.get_root_topic()
    root_topic.set_title("root node")
    sub_topic = root_topic.add_sub_topic()
    sub_topic.set_title("sub topic")
    root_topic.add_marker(MarkerId.starRed)

    xmind.save(workbook, path=path)
    assert zipfile.is_zipfile(path)

    reloaded = xmind.load(path)
    reloaded_sheet = reloaded.get_primary_sheet()
    assert reloaded_sheet.get_title() == "first sheet"

    reloaded_root = reloaded_sheet.get_root_topic()
    assert reloaded_root.get_title() == "root node"
    assert [t.get_title() for t in reloaded_root.get_sub_topics()] == ["sub topic"]


def test_deprecated_camel_case_methods_delegate_to_snake_case(tmp_path):
    workbook = xmind.load(str(tmp_path / "alias.xmind"))
    with pytest.warns(DeprecationWarning, match="getPrimarySheet"):
        sheet = workbook.getPrimarySheet()
    sheet.setTitle("via camelCase")

    assert sheet.get_title() == sheet.getTitle() == "via camelCase"

    root_topic = sheet.get_root_topic()
    with pytest.warns(DeprecationWarning, match="setTitle"):
        root_topic.setTitle("deprecated title")
    with pytest.warns(DeprecationWarning, match="addMarker"):
        root_topic.addMarker(MarkerId.starRed)
    assert root_topic.get_title() == "deprecated title"
