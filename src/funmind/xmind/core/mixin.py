from . import Element
from . import const
from .. import utils


class WorkbookMixinElement(Element):
    """`WorkbookMixinElement` 是隶属于某个工作簿的 XMind 文档元素基类。
    """

    def __init__(self, node=None, ownerWorkbook=None) -> None:
        super(WorkbookMixinElement, self).__init__(node)
        self._owner_workbook = ownerWorkbook
        self.registerOwnerWorkbook()

    def registerOwnerWorkbook(self) -> None:
        """将当前元素挂载到所属工作簿的 DOM 文档上。"""
        if self._owner_workbook:
            self.setOwnerDocument(self._owner_workbook.getOwnerDocument())

    def updateModifiedTime(self) -> "WorkbookMixinElement":
        """将最后修改时间刷新为当前时间，并返回当前元素。"""
        self.setModifiedTime(utils.get_current_time())
        return self

    def setOwnerWorkbook(self, workbook) -> None:
        """设置所属工作簿；仅在尚未设置过时生效。"""
        if not self._owner_workbook:
            self._owner_workbook = workbook

    def setModifiedTime(self, time: int) -> None:
        """设置最后修改时间戳（毫秒）。"""
        self.setAttribute(const.ATTR_TIMESTAMP, int(time))

    def getOwnerWorkbook(self):
        """返回所属的 `WorkbookDocument`，未设置时返回 ``None``。"""
        return self._owner_workbook

    def getModifiedTime(self) -> str | None:
        """返回可读形式的最后修改时间，未设置时返回 ``None``。"""
        timestamp = self.getAttribute(const.ATTR_TIMESTAMP)
        if timestamp:
            return utils.readable_time(timestamp)

    def getID(self) -> str | None:
        """返回元素 id。"""
        return self.getAttribute(const.ATTR_ID)


class TopicMixinElement(Element):
    """`TopicMixinElement` 是隶属于某个主题的 XMind 文档元素基类（如备注、标签）。
    """

    def __init__(self, node=None, ownerTopic=None) -> None:
        super(TopicMixinElement, self).__init__(node)
        self._owner_topic = ownerTopic

    def getOwnerTopic(self):
        """返回所属的 `TopicElement`，未设置时返回 ``None``。"""
        return self._owner_topic

    def getOwnerSheet(self):
        """返回所属主题所在的工作表，未设置所属主题时返回 ``None``。"""
        if not self._owner_topic:
            return

        return self._owner_topic.getOwnerSheet()

    def getOwnerWorkbook(self):
        """返回所属主题所在的工作簿，未设置所属主题时返回 ``None``。"""
        if not self._owner_topic:
            return

        return self._owner_topic.getOwnerWorkbook()
