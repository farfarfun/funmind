"""补充公开 API 的正常路径/边界测试：批注、备注、标签、关系线、超链接、附件、路径安全。"""
import os
import warnings
import zipfile

import pytest

from funmind import xmind
from funmind.xmind.core import const
from funmind.xmind.core.markerref import MarkerId
from funmind.xmind.core.saver import WorkbookSaver


def _new_workbook_with_root(tmp_path, name="demo.xmind"):
    path = str(tmp_path / name)
    workbook = xmind.load(path)
    sheet = workbook.get_primary_sheet()
    root_topic = sheet.get_root_topic()
    root_topic.set_title("root")
    return workbook, sheet, root_topic


def test_comment_add_and_get(tmp_path):
    """正常路径：为主题添加批注后可读取；同一主题多条批注按换行拼接。"""
    workbook, _, root_topic = _new_workbook_with_root(tmp_path)

    root_topic.addComment("第一条批注", author="alice")
    root_topic.addComment("第二条批注")

    assert root_topic.getComments() == "第一条批注\n第二条批注"
    comments = workbook.commentsbook.getComments()
    assert comments[0].getAuthor() == "alice"
    assert comments[1].getAuthor() == "admin"


def test_camel_case_api_warns_and_snake_case_api_does_not(tmp_path):
    """兼容接口：旧驼峰入口告警，snake_case 入口保持为正式 API。"""
    _, sheet, _ = _new_workbook_with_root(tmp_path)

    with pytest.deprecated_call(match="setTitle 已弃用"):
        sheet.setTitle("legacy")

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        sheet.set_title("current")
    assert not recorded


def test_comment_invalid_object_id_rejected():
    """边界/失败路径：批注关联的主题 id 长度不合法时必须拒绝。"""
    from funmind.xmind.core.comments import CommentElement

    comment = CommentElement(content="x")
    with pytest.raises(ValueError):
        comment.setObjectId("too-short-id")


def test_notes_set_and_get(tmp_path):
    """正常路径：设置纯文本备注后可读取；未设置时返回 None。"""
    _, _, root_topic = _new_workbook_with_root(tmp_path)

    assert root_topic.getNotes() is None

    root_topic.setPlainNotes("这是一条备注")
    assert root_topic.getNotes() == "这是一条备注"


def test_labels_add_and_get(tmp_path):
    """正常路径：设置标签后可读取；未设置时返回 None。"""
    _, _, root_topic = _new_workbook_with_root(tmp_path)

    assert root_topic.getLabels() is None

    root_topic.addLabel("重要")
    assert root_topic.getLabels() == "重要"


def test_relationship_create_and_remove(tmp_path):
    """正常路径：在同一工作表下创建、查询、删除关系线。"""
    _, sheet, root_topic = _new_workbook_with_root(tmp_path)
    child1 = root_topic.add_sub_topic()
    child1.set_title("child1")
    child2 = root_topic.add_sub_topic()
    child2.set_title("child2")

    rel = sheet.createRelationship(child1.getID(), child2.getID(), title="关联")
    assert rel.getTitle() == "关联"
    assert rel.getEnd1().getTitle() == "child1"
    assert rel.getEnd2().getTitle() == "child2"
    assert len(sheet.getRelationships()) == 1

    sheet.removeRelationship(rel)
    assert sheet.getRelationships() == []


def test_relationship_cross_sheet_rejected(tmp_path):
    """失败路径：跨工作表创建关系线必须抛出 WorkbookError。"""
    from funmind.xmind.exceptions import WorkbookError

    workbook, _sheet1, root_topic1 = _new_workbook_with_root(tmp_path)
    sheet2 = workbook.createSheet()
    root_topic2 = sheet2.getRootTopic()

    with pytest.raises(WorkbookError):
        workbook.createRelationship(root_topic1, root_topic2)


def test_hyperlink_file_topic_and_url(tmp_path):
    """正常路径：文件、主题、URL 三种超链接设置后均可正确读取协议前缀。"""
    _, _, root_topic = _new_workbook_with_root(tmp_path)
    assert root_topic.getHyperlink() is None

    target_file = tmp_path / "a.txt"
    root_topic.setFileHyperlink(str(target_file))
    assert root_topic.getHyperlink().startswith(const.FILE_PROTOCOL)

    root_topic.setTopicHyperlink("#" + "a" * 26)
    assert root_topic.getHyperlink() == const.TOPIC_PROTOCOL + "a" * 26

    root_topic.setURLHyperlink("example.com")
    assert root_topic.getHyperlink() == const.HTTP_PROTOCOL + "example.com"


def test_style_elements_round_trip(tmp_path):
    """正常路径：主题设置样式 id 后，样式文档保存/重新加载仍可读到元素（回归上游"建了却读不到"的逻辑写反问题）。"""
    workbook, _, root_topic = _new_workbook_with_root(tmp_path)
    root_topic.setStyleID()
    style_id = root_topic.getStyleId()
    assert style_id

    path = str(tmp_path / "styled.xmind")
    xmind.save(workbook, path=path)
    reloaded = xmind.load(path)
    assert reloaded.get_primary_sheet().get_root_topic().getStyleId() == style_id
    # getStyleElements 此前存在逻辑写反：找到样式节点时反而返回 None。
    assert reloaded.stylesbook.getStyleElements() == []


def test_marker_add_replace_same_family(tmp_path):
    """正常路径：同一分类的标记会被替换，而不是重复添加。"""
    _, _, root_topic = _new_workbook_with_root(tmp_path)
    root_topic.add_marker(MarkerId.starRed)
    root_topic.add_marker(MarkerId.starBlue)

    markers = root_topic.getMarkers()
    assert len(markers) == 1
    # MarkerId.starBlue 等常量本身是裸字符串（而非 MarkerId 实例），
    # 故与 getMarkerId() 返回的 MarkerId 实例比较时需转换为字符串。
    assert str(markers[0].getMarkerId()) == MarkerId.starBlue


def test_save_with_attachments_round_trip(tmp_path):
    """正常路径：工作簿携带附件时，默认保存会保留附件；except_attachments=True 时会跳过。"""
    source_path = tmp_path / "with_attachment.xmind"
    with zipfile.ZipFile(source_path, "w") as zf:
        zf.writestr(const.CONTENT_XML, "<xmap-content/>")
        zf.writestr(const.STYLES_XML, "<xmap-styles/>")
        zf.writestr(const.COMMENTS_XML, "<comments/>")
        zf.writestr("attachments/pic.png", b"fake-image-bytes")

    workbook = xmind.load(str(source_path))

    kept_path = str(tmp_path / "kept.xmind")
    xmind.save(workbook, path=kept_path)
    with zipfile.ZipFile(kept_path) as zf:
        assert "attachments/pic.png" in zf.namelist()

    skipped_path = str(tmp_path / "skipped.xmind")
    xmind.save(workbook, path=skipped_path, except_attachments=True)
    with zipfile.ZipFile(skipped_path) as zf:
        assert "attachments/pic.png" not in zf.namelist()


def test_save_rejects_zip_path_traversal(tmp_path):
    """安全边界：恶意压缩包中的 "../" 或绝对路径成员名不得写出到临时目录之外。"""
    source_path = tmp_path / "malicious.xmind"
    escape_marker = tmp_path.parent / "funmind_zip_slip_poc.txt"
    if escape_marker.exists():
        escape_marker.unlink()

    with zipfile.ZipFile(source_path, "w") as zf:
        zf.writestr(const.CONTENT_XML, "<xmap-content/>")
        zf.writestr(const.STYLES_XML, "<xmap-styles/>")
        zf.writestr(const.COMMENTS_XML, "<comments/>")
        # 相对路径穿越：尝试逃逸到 reference_dir 的上两级目录。
        zf.writestr("../../funmind_zip_slip_poc.txt", b"pwned")
        # 绝对路径成员名：尝试直接写到任意绝对路径。
        zf.writestr(os.path.join(str(tmp_path), "funmind_zip_slip_abs.txt").lstrip(os.sep), b"pwned")

    workbook = xmind.load(str(source_path))
    out_path = str(tmp_path / "saved.xmind")

    # 保存过程不应抛异常，也不应在仓库之外留下文件。
    xmind.save(workbook, path=out_path)

    assert not escape_marker.exists()
    with zipfile.ZipFile(out_path) as zf:
        names = zf.namelist()
        assert not any(".." in n for n in names)


def test_saver_get_reference_blocks_absolute_member_name(tmp_path):
    """直接针对 WorkbookSaver._get_reference 的单元级校验：绝对路径成员必须被拒绝。"""
    source_path = tmp_path / "abs_member.xmind"
    target_outside = tmp_path / "outside_marker.txt"
    if target_outside.exists():
        target_outside.unlink()

    with zipfile.ZipFile(source_path, "w") as zf:
        zf.writestr(const.CONTENT_XML, "<xmap-content/>")
        zf.writestr(const.STYLES_XML, "<xmap-styles/>")
        zf.writestr(const.COMMENTS_XML, "<comments/>")
        zf.writestr(str(target_outside), b"pwned")

    workbook = xmind.load(str(source_path))
    saver = WorkbookSaver(workbook)
    reference_dir = saver._get_reference()

    assert not target_outside.exists()
    # reference_dir 内不应包含以绝对路径写入的恶意文件。
    for _, _, filenames in os.walk(reference_dir):
        assert "outside_marker.txt" not in filenames
