from . import const
from .mixin import WorkbookMixinElement


class TitleElement(WorkbookMixinElement):
    """表示工作簿、工作表或主题的标题 XML 元素。"""
    TAG_NAME = const.TAG_TITLE

    def __init__(self, node=None, ownerWorkbook=None):
        super(TitleElement, self).__init__(node, ownerWorkbook)
