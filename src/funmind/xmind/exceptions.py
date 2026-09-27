class XMindError(Exception):
    """funmind 内所有自定义异常的基类。"""


class InvalidXMindFileError(XMindError):
    """XMind 文件路径不合法（如缺少 `.xmind` 扩展名）时抛出。"""


class WorkbookError(XMindError):
    """构造或操作 `WorkbookDocument` 时出现非法状态时抛出。"""
