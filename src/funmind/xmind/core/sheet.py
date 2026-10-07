from funmind.xmind import utils

from . import const
from .mixin import WorkbookMixinElement
from .relationship import RelationshipElement, RelationshipsElement
from .title import TitleElement
from .topic import TopicElement


class SheetElement(WorkbookMixinElement):
    """表示 XMind 工作簿中的一个工作表及其根主题。"""
    TAG_NAME = const.TAG_SHEET

    def __init__(self, node=None, ownerWorkbook=None):
        super(SheetElement, self).__init__(node, ownerWorkbook)

        self.addIdAttribute(const.ATTR_ID)
        self.setAttribute(const.ATTR_TIMESTAMP, int(utils.get_current_time()))
        self._root_topic = self._get_root_topic()

    def _get_root_topic(self) -> TopicElement:
        # 初始化根主题：若 DOM 中尚无根主题节点则新建一个。
        topics = self.getChildNodesByTagName(const.TAG_TOPIC)
        owner_workbook = self.getOwnerWorkbook()
        if len(topics) >= 1:
            root_topic = topics[0]
            root_topic = TopicElement(root_topic, owner_workbook)
        else:
            root_topic = TopicElement(ownerWorkbook=owner_workbook)
            self.appendChild(root_topic)

        return root_topic

    def _getRelationships(self):
        return self.getFirstChildNodeByTagName(const.TAG_RELATIONSHIPS)

    def _addRelationship(self, rel: RelationshipElement) -> None:
        """将关系线添加到工作表。"""
        _rels = self._getRelationships()
        owner_workbook = self.getOwnerWorkbook()

        rels = RelationshipsElement(_rels, owner_workbook)

        if not _rels:
            self.appendChild(rels)

        rels.appendChild(rel)

    def updateModifiedTime(self) -> "SheetElement":
        """更新工作表（及其所属工作簿）的最后修改时间，并返回当前工作表。"""
        super(SheetElement, self).updateModifiedTime()

        workbook = self.getParent()
        if workbook:
            workbook.updateModifiedTime()

        return self

    def setTitle(self, text: str) -> "SheetElement":
        """设置工作表标题并返回当前工作表。"""
        _title = self._get_title()
        title = TitleElement(_title, self.getOwnerWorkbook())
        title.setTextContent(text)

        if _title is None:
            self.appendChild(title)

        return self.updateModifiedTime()

    def createRelationship(
        self, end1: "TopicElement | str", end2: "TopicElement | str", title: str | None = None
    ) -> RelationshipElement:
        """在两个主题之间创建关系线，新建的关系线会自动添加到当前工作表。

        :param end1: 起点主题对象或其 id。
        :param end2: 终点主题对象或其 id。
        :param title: 关系线标题，默认为空。
        :return: 新建的 `RelationshipElement` 实例。
        """
        rel = RelationshipElement(ownerWorkbook=self.getOwnerWorkbook())
        rel.setEnd1ID(end1 if isinstance(end1, str) else end1.getID())
        rel.setEnd2ID(end2 if isinstance(end2, str) else end2.getID())

        if title is not None:
            rel.setTitle(title)

        self._addRelationship(rel)

        return rel

    def getRelationships(self) -> list[RelationshipElement]:
        """返回当前工作表下的全部关系线，没有则返回空列表。"""
        _rels = self._getRelationships()
        if not _rels:
            return []
        owner_workbook = self.getOwnerWorkbook()
        return RelationshipsElement(_rels, owner_workbook).getRelationships()

    def removeRelationship(self, rel: RelationshipElement) -> None:
        """从工作表中移除一条关系线。"""
        rels = self._getRelationships()

        if not rels:
            return

        rel = rel.getImplementation()
        rels.removeChild(rel)
        if not rels.hasChildNodes():
            self.getImplementation().removeChild(rels)

        self.updateModifiedTime()

    def getRootTopic(self) -> TopicElement:
        """返回工作表的根主题。"""
        return self._root_topic

    def _get_title(self):
        return self.getFirstChildNodeByTagName(const.TAG_TITLE)

    # FIXME: convert to getter/setter
    def getTitle(self) -> str | None:
        """返回工作表标题文本，未设置时返回 ``None``。"""
        title = self._get_title()
        if title:
            title = TitleElement(title, self.getOwnerWorkbook())
            return title.getTextContent()

    def getParent(self):
        """返回工作表所属的 `WorkbookDocument`，不属于任何工作簿时返回 ``None``。"""
        workbook = self.getOwnerWorkbook()
        if workbook:
            parent = self.getParentNode()

            if parent == workbook.getWorkbookElement().getImplementation():
                return workbook

    def getData(self) -> dict:
        """以字典形式返回工作表的主要内容（含根主题的递归数据）。"""
        root_topic = self.getRootTopic()
        data = {
            'id': self.getAttribute(const.ATTR_ID),
            'title': self.getTitle(),
            'topic': root_topic.getData()
        }
        return data


utils.add_snake_case_aliases(SheetElement)
