from . import const
from .mixin import WorkbookMixinElement


class TitleElement(WorkbookMixinElement):
    TAG_NAME = const.TAG_TITLE

    def __init__(self, node=None, ownerWorkbook=None):
        super(TitleElement, self).__init__(node, ownerWorkbook)
