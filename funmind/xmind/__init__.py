from funmind.xmind.core.loader import WorkbookLoader
from funmind.xmind.core.saver import WorkbookSaver


def load(path: str):
    """从指定路径加载 XMind 工作簿。

    :param path: `.xmind` 文件路径。文件不存在或已损坏时按空工作簿处理，不会抛出异常；
        但文件名缺少 `.xmind` 扩展名时会抛出 `InvalidXMindFileError`。
    :return: `WorkbookDocument` 对象。
    """
    loader = WorkbookLoader(path)
    return loader.get_workbook()


def save(workbook, path=None, only_content=False, except_attachments=False, except_revisions=False):
    """将工作簿保存为 `.xmind` 文件。

    :param workbook: 待保存的 `WorkbookDocument` 对象。
    :param path: 保存路径；不传则保存到 workbook 自身记录的路径。
    :param only_content: 仅保存 content.xml。
    :param except_attachments: 仅保存 content.xml、styles.xml、comments.xml，不携带附件。
    :param except_revisions: 是否跳过 Revisions 内容以节省空间。
    """
    saver = WorkbookSaver(workbook)
    saver.save(path=path, only_content=only_content, except_attachments=except_attachments,
               except_revisions=except_revisions)
