from funmind.xmind import utils

from . import const
from .mixin import WorkbookMixinElement
from .title import TitleElement
from .topic import TopicElement


class RelationshipElement(WorkbookMixinElement):
    """表示同一工作表内两个主题之间的关系线。"""
    TAG_NAME = const.TAG_RELATIONSHIP

    def __init__(self, node=None, ownerWorkbook=None):
        super(RelationshipElement, self).__init__(node, ownerWorkbook)

        self.addIdAttribute(const.ATTR_ID)
        self.setAttribute(const.ATTR_TIMESTAMP, int(utils.get_current_time()))

    def _get_title(self):
        return self.getFirstChildNodeByTagName(const.TAG_TITLE)

    def _find_end_point(self, id):
        owner_workbook = self.getOwnerWorkbook()
        if owner_workbook is None:
            return

        end_point = owner_workbook.getElementById(id)
        if end_point is None:
            return

        if end_point.tagName == const.TAG_TOPIC:
            return TopicElement(end_point, owner_workbook)

    # FIXME: Convert the following to getter/setter
    def setEnd1ID(self, id: str) -> "RelationshipElement":
        """设置关系线起点主题的 id，并返回当前关系线。"""
        self.setAttribute(const.ATTR_END1, id)
        return self.updateModifiedTime()

    def setEnd2ID(self, id: str) -> "RelationshipElement":
        """设置关系线终点主题的 id，并返回当前关系线。"""
        self.setAttribute(const.ATTR_END2, id)
        return self.updateModifiedTime()

    def setTitle(self, text: str) -> "RelationshipElement":
        """设置关系线标题，并返回当前关系线。"""
        _title = self._get_title()
        title = TitleElement(_title, self.getOwnerWorkbook())
        title.setTextContent(text)

        if _title is None:
            self.appendChild(title)

        return self.updateModifiedTime()

    def getEnd1ID(self) -> str | None:
        """返回关系线起点主题的 id。"""
        return self.getAttribute(const.ATTR_END1)

    def getEnd2ID(self) -> str | None:
        """返回关系线终点主题的 id。"""
        return self.getAttribute(const.ATTR_END2)

    def getEnd1(self) -> "TopicElement | None":
        """返回关系线起点对应的主题对象，找不到时返回 ``None``。"""
        return self._find_end_point(self.getEnd1ID())

    def getEnd2(self) -> "TopicElement | None":
        """返回关系线终点对应的主题对象，找不到时返回 ``None``。"""
        return self._find_end_point(self.getEnd2ID())

    def getTitle(self) -> str | None:
        """返回关系线标题文本，未设置时返回 ``None``。"""
        title = self._get_title()
        if title:
            title = TitleElement(title, self.getOwnerWorkbook())
            return title.getTextContent()


class RelationshipsElement(WorkbookMixinElement):
    """表示工作表中全部关系线的容器。"""
    TAG_NAME = const.TAG_RELATIONSHIPS

    def __init__(self, node=None, ownerWorkbook=None):
        super(RelationshipsElement, self).__init__(node, ownerWorkbook)

    def getRelationships(self) -> list["RelationshipElement"]:
        """列出全部关系线。"""
        relationships = []
        owner_workbook = self.getOwnerWorkbook()
        for r in self.getChildNodesByTagName(const.TAG_RELATIONSHIP):
            relationships.append(RelationshipElement(r, owner_workbook))

        return relationships


utils.add_snake_case_aliases(RelationshipElement)
utils.add_snake_case_aliases(RelationshipsElement)
