import warnings
from typing import TYPE_CHECKING

from . import const
from .labels import LabelsElement, LabelElement
from .markerref import MarkerId
from .markerref import MarkerRefElement
from .markerref import MarkerRefsElement
from .mixin import WorkbookMixinElement
from .notes import NotesElement, PlainNotes
from .position import PositionElement
from .title import TitleElement
from .. import utils

if TYPE_CHECKING:
    # 仅用于类型标注；`sheet.py` 反过来会导入本模块的 `TopicElement`，
    # 直接在模块顶层导入会造成循环导入，因此放在 TYPE_CHECKING 下。
    from .sheet import SheetElement


def split_hyperlink(hyperlink: str) -> tuple[str | None, str]:
    """将超链接拆分为协议前缀和内容两部分。

    :param hyperlink: 完整的超链接字符串，如 ``file:///tmp/a.txt``。
    :return: ``(protocol, content)``；协议不存在时 ``protocol`` 为 ``None``。
    """
    colon = hyperlink.find(":")
    if colon < 0:
        protocol = None
    else:
        protocol = hyperlink[:colon]

    hyperlink = hyperlink[colon + 1:]
    while hyperlink.startswith("/"):
        hyperlink = hyperlink[1:]

    return protocol, hyperlink


class TopicElement(WorkbookMixinElement):
    TAG_NAME = const.TAG_TOPIC

    def __init__(self, node=None, ownerWorkbook=None):
        super(TopicElement, self).__init__(node, ownerWorkbook)

        self.addIdAttribute(const.ATTR_ID)
        self.setAttribute(const.ATTR_TIMESTAMP, int(utils.get_current_time()))

    def _set_hyperlink(self, hyperlink):
        self.setAttribute(const.ATTR_HREF, hyperlink)
        # self.updateModifiedTime()

    def set_title(self, text: str) -> "TopicElement":
        """设置主题标题并返回当前主题。"""
        _title = self._get_title()
        title = TitleElement(_title, self.getOwnerWorkbook())
        title.setTextContent(text)

        if _title is None:
            self.appendChild(title)

        # self.updateModifiedTime()
        return self

    def setTitle(self, text: str) -> "TopicElement":
        """兼容旧接口，请改用 :meth:`set_title`。"""
        warnings.warn(
            "setTitle 已弃用，请改用 set_title，将于 1.0 移除",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_title(text)

    def setPlainNotes(self, content: str) -> PlainNotes:
        """为主题设置纯文本备注。"""
        new = PlainNotes(content, None, self)
        _notes = self._get_notes()
        if not _notes:
            tmp = NotesElement(None, self)
            self.appendChild(tmp)
        else:
            tmp = NotesElement(_notes, self)
            old = tmp.getFirstChildNodeByTagName(new.getFormat())
            if old:
                tmp.getImplementation().removeChild(old)

        tmp.appendChild(new)
        return new

    def _get_title(self):
        return self.getFirstChildNodeByTagName(const.TAG_TITLE)

    def _get_markerrefs(self):
        return self.getFirstChildNodeByTagName(const.TAG_MARKERREFS)

    def _get_labels(self):
        return self.getFirstChildNodeByTagName(const.TAG_LABELS)

    def _get_notes(self):
        return self.getFirstChildNodeByTagName(const.TAG_NOTES)

    def _get_position(self):
        return self.getFirstChildNodeByTagName(const.TAG_POSITION)

    def _get_children(self):
        return self.getFirstChildNodeByTagName(const.TAG_CHILDREN)

    def getOwnerSheet(self) -> "SheetElement | None":
        """返回当前主题所属的工作表，找不到时返回 ``None``。"""
        parent = self.getParentNode()

        while parent and parent.tagName != const.TAG_SHEET:
            parent = parent.parentNode

        if not parent:
            return

        owner_workbook = self.getOwnerWorkbook()
        if not owner_workbook:
            return

        for sheet in owner_workbook.getSheets():
            if parent is sheet.getImplementation():
                return sheet

    def getTitle(self) -> str | None:
        """返回主题标题文本，未设置时返回 ``None``。"""
        title = self._get_title()
        if title:
            title = TitleElement(title, self.getOwnerWorkbook())
            return title.getTextContent()

    def getMarkers(self) -> list["MarkerRefElement"]:
        """返回当前主题上的全部标记（marker），没有则返回空列表。"""
        refs = self._get_markerrefs()
        if not refs:
            return []
        tmp = MarkerRefsElement(refs, self.getOwnerWorkbook())
        markers = tmp.getChildNodesByTagName(const.TAG_MARKERREF)
        marker_list = []
        if markers:
            for i in markers:
                marker_list.append(MarkerRefElement(i, self.getOwnerWorkbook()))
        return marker_list

    def add_marker(self, marker_id: MarkerId | str) -> MarkerRefElement | None:
        """为主题添加标记，并返回对应的标记元素。"""
        if not marker_id:
            return None
        if isinstance(marker_id, str):
            marker_id = MarkerId(marker_id)

        refs = self._get_markerrefs()
        if not refs:
            tmp = MarkerRefsElement(None, self.getOwnerWorkbook())
            self.appendChild(tmp)
        else:
            tmp = MarkerRefsElement(refs, self.getOwnerWorkbook())
        markers = tmp.getChildNodesByTagName(const.TAG_MARKERREF)

        # If the same family marker exists, replace it
        if markers:
            for m in markers:
                mre = MarkerRefElement(m, self.getOwnerWorkbook())
                # 找到同类标记时替换原标记。
                if mre.getMarkerId().getFamily() == marker_id.getFamily():
                    mre.setMarkerId(marker_id)
                    return mre
        # 没有同类标记时追加新标记。
        mre = MarkerRefElement(None, self.getOwnerWorkbook())
        mre.setMarkerId(marker_id)
        tmp.appendChild(mre)
        return mre

    def addMarker(self, markerId: MarkerId | str) -> MarkerRefElement | None:
        """兼容旧接口，请改用 :meth:`add_marker`。"""
        warnings.warn(
            "addMarker 已弃用，请改用 add_marker，将于 1.0 移除",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_marker(markerId)

    def getLabels(self) -> str | None:
        """返回主题的标签内容；当前每个主题只支持设置一个标签。"""
        _labels = self._get_labels()
        if not _labels:
            return None
        tmp = LabelsElement(_labels, self)
        # labels = tmp.getChildNodesByTagName(const.TAG_LABEL)
        # label_list = []
        # if labels:
        #     for i in labels:
        #         label_list.append(LabelElement(i, self.getOwnerWorkbook()))
        # return label_list

        label = LabelElement(node=tmp.getFirstChildNodeByTagName(const.TAG_LABEL), ownerTopic=self)
        content = label.getLabel()
        return content

    def addLabel(self, content: str) -> LabelElement:
        """为主题设置标签内容（已存在时覆盖），并返回标签元素。"""
        _labels = self._get_labels()
        if not _labels:
            tmp = LabelsElement(None, self)
            self.appendChild(tmp)
        else:
            tmp = LabelsElement(_labels, self)
            old = tmp.getFirstChildNodeByTagName(const.TAG_LABEL)
            if old:
                tmp.getImplementation().removeChild(old)

        label = LabelElement(content, None, self)
        tmp.appendChild(label)
        return label

    def getComments(self) -> str | None:
        """返回当前主题关联的全部批注内容（已按换行拼接），没有则返回 ``None``。"""
        topic_id = self.getAttribute(const.ATTR_ID)
        workbook = self.getOwnerWorkbook()
        content = workbook.commentsbook.getComment(topic_id)
        return content

    def addComment(self, content: str, author: str | None = None):
        """为当前主题新增一条批注，返回新建的批注元素。

        :param content: 批注正文内容。
        :param author: 批注作者，不传则记为 ``admin``。
        """
        topic_id = self.getAttribute(const.ATTR_ID)
        workbook = self.getOwnerWorkbook()
        comment = workbook.commentsbook.addComment(content=content, topic_id=topic_id, author=author)
        return comment

    def getNotes(self) -> str | None:
        """返回主题的纯文本备注内容；当前每个主题只支持设置一条备注。"""
        _notes = self._get_notes()
        if not _notes:
            return None
        tmp = NotesElement(_notes, self)
        # 目前只支持纯文本格式的备注。
        content = tmp.getContent(const.PLAIN_FORMAT_NOTE)
        return content

    def setFolded(self) -> None:
        """将主题标记为折叠分支。"""
        self.setAttribute(const.ATTR_BRANCH, const.VAL_FOLDED)

        # self.updateModifiedTime()

    def getPosition(self) -> tuple[int, int] | None:
        """返回主题的自由定位坐标 ``(x, y)``；未设置坐标时返回 ``None``。"""
        position = self._get_position()
        if position is None:
            return

        position = PositionElement(position, self.getOwnerWorkbook())

        x = position.getX()
        y = position.getY()

        if x is None and y is None:
            return

        x = x or 0
        y = y or 0

        return int(x), int(y)

    def setPosition(self, x: int, y: int) -> "TopicElement":
        """设置主题的自由定位坐标，并返回当前主题。"""
        owner_workbook = self.getOwnerWorkbook()
        position = self._get_position()

        if not position:
            position = PositionElement(ownerWorkbook=owner_workbook)
            self.appendChild(position)
        else:
            position = PositionElement(position, owner_workbook)

        position.setX(x)
        position.setY(y)
        return self
        # self.updateModifiedTime()

    def removePosition(self) -> None:
        """移除主题的自由定位坐标。"""
        position = self._get_position()
        if position is not None:
            self.getImplementation().removeChild(position)
        # self.updateModifiedTime()

    def getType(self) -> str | None:
        """返回主题类型：根主题为 ``root``，子主题为 ``attached`` 或 ``detached``。"""
        parent = self.getParentNode()
        if not parent:
            return

        if parent.tagName == const.TAG_SHEET:
            return const.TOPIC_ROOT

        if parent.tagName == const.TAG_TOPICS:
            topics = TopicsElement(parent, self.getOwnerWorkbook())
            return topics.getType()

    def getTopics(self, topics_type: str = const.TOPIC_ATTACHED) -> "TopicsElement | None":
        """返回指定类型（附加/分离）的子主题容器，不存在时返回 ``None``。"""
        topic_children = self._get_children()

        if topic_children:
            topic_children = ChildrenElement(topic_children, self.getOwnerWorkbook())

            return topic_children.getTopics(topics_type)

    def getSubTopics(self, topics_type: str = const.TOPIC_ATTACHED) -> list["TopicElement"]:
        """列出当前主题下所有子主题，没有则返回空列表。"""
        topics = self.getTopics(topics_type)
        if not topics:
            return []

        return topics.getSubTopics()

    def getSubTopicByIndex(self, index: int, topics_type: str = const.TOPIC_ATTACHED):
        """按索引获取指定子主题；索引越界时返回完整子主题列表。"""
        sub_topics = self.getSubTopics(topics_type)
        if sub_topics is None:
            return

        if index < 0 or index >= len(sub_topics):
            return sub_topics

        return sub_topics[index]

    def addSubTopic(
        self,
        topic: "TopicElement | None" = None,
        index: int = -1,
        topics_type: str = const.TOPIC_ATTACHED,
    ) -> "TopicElement":
        """为当前主题添加一个子主题，并返回新增的子主题。

        :param topic: 待添加的 `TopicElement` 对象；不传则自动新建一个。
        :param index: 插入位置索引；不传或越界则追加到子主题列表末尾，
            否则插入到该索引对应子主题之前。
        :param topics_type: 子主题类型，`TOPIC_ATTACHED`（附加）或 `TOPIC_DETACHED`（分离）。
        """
        owner_workbook = self.getOwnerWorkbook()
        topic = topic or self.__class__(None, owner_workbook)

        topic_children = self._get_children()
        if not topic_children:
            topic_children = ChildrenElement(ownerWorkbook=owner_workbook)
            self.appendChild(topic_children)
        else:
            topic_children = ChildrenElement(topic_children, owner_workbook)

        topics = topic_children.getTopics(topics_type)
        if not topics:
            topics = TopicsElement(ownerWorkbook=owner_workbook)
            topics.setAttribute(const.ATTR_TYPE, topics_type)
            topic_children.appendChild(topics)

        topic_list = []
        for i in topics.getChildNodesByTagName(const.TAG_TOPIC):
            topic_list.append(TopicElement(i, owner_workbook))

        if index < 0 or index >= len(topic_list):
            topics.appendChild(topic)
        else:
            topics.insertBefore(topic, topic_list[index])

        return topic

    def getIndex(self) -> int:
        """返回当前主题在同级子主题列表中的索引；不是子主题（无父 `topics` 节点）时返回 -1。"""
        parent = self.getParentNode()
        if parent and parent.tagName == const.TAG_TOPICS:
            index = 0
            for child in parent.childNodes:
                if self.getImplementation() == child:
                    return index
                index += 1
        return -1

    def getHyperlink(self) -> str | None:
        """返回主题的超链接地址，未设置时返回 ``None``。"""
        return self.getAttribute(const.ATTR_HREF)

    def setFileHyperlink(self, path: str) -> None:
        """将主题超链接设置为本地文件。

        :param path: 目标文件路径。
        """
        protocol, content = split_hyperlink(path)
        if not protocol:
            path = const.FILE_PROTOCOL + utils.get_abs_path(path)

        self._set_hyperlink(path)

    def setTopicHyperlink(self, tid: str) -> None:
        """将主题超链接设置为指向另一个主题。

        :param tid: 目标主题的 id。
        """
        protocol, content = split_hyperlink(tid)
        if not protocol:
            if tid.startswith("#"):
                tid = tid[1:]

            tid = const.TOPIC_PROTOCOL + tid
        self._set_hyperlink(tid)

    def setURLHyperlink(self, url: str) -> None:
        """将主题超链接设置为指定网址。

        :param url: 目标 HTTP(S) 网址。
        """
        protocol, content = split_hyperlink(url)
        if not protocol:
            url = const.HTTP_PROTOCOL + content

        self._set_hyperlink(url)

    def getStructureClass(self) -> str | None:
        """返回主题的结构样式类名（如未设置返回 ``None``）。"""
        return self.getAttribute(const.ATTR_STRUCTURE_CLASS)

    def setStructureClass(self, structure_class: str) -> None:
        """设置主题的结构样式类名。

        :param structure_class: 结构类名，如 ``structure-class="org.xmind.ui.map.floating"``。
        """
        self.setAttribute(const.ATTR_STRUCTURE_CLASS, structure_class)

    def getStyleId(self) -> str | None:
        """返回主题关联的样式 id（如未设置返回 ``None``）。"""
        return self.getAttribute(const.ATTR_STYLE_ID)

    def setStyleID(self) -> None:
        """为主题生成并设置一个新的随机样式 id。"""
        style_id = utils.generate_id()
        self.setAttribute(const.ATTR_STYLE_ID, style_id)

    def getData(self) -> dict:
        """以字典形式返回主题的全部内容；若存在子主题则递归展开。"""
        data = {
            'id': self.getAttribute(const.ATTR_ID),
            'link': self.getAttribute(const.ATTR_HREF),
            'title': self.getTitle(),
            'note': self.getNotes(),
            'label': self.getLabels(),
            'comment': self.getComments(),
            'markers': [marker.getMarkerId().name for marker in self.getMarkers() if marker],
        }

        if self.getSubTopics(topics_type=const.TOPIC_ATTACHED):
            data['topics'] = []
            for sub_topic in self.getSubTopics(topics_type=const.TOPIC_ATTACHED):
                data['topics'].append(sub_topic.getData())

        return data


utils.add_snake_case_aliases(TopicElement)


class ChildrenElement(WorkbookMixinElement):
    TAG_NAME = const.TAG_CHILDREN

    def __init__(self, node=None, ownerWorkbook=None):
        super(ChildrenElement, self).__init__(node, ownerWorkbook)

    def getTopics(self, topics_type: str) -> "TopicsElement | None":
        """返回指定类型的子主题容器，不存在时返回 ``None``。"""
        topics = self.iterChildNodesByTagName(const.TAG_TOPICS)
        for i in topics:
            t = TopicsElement(i, self.getOwnerWorkbook())
            if topics_type == t.getType():
                return t


class TopicsElement(WorkbookMixinElement):
    TAG_NAME = const.TAG_TOPICS

    def __init__(self, node=None, ownerWorkbook=None):
        super(TopicsElement, self).__init__(node, ownerWorkbook)

    def getType(self) -> str | None:
        """返回子主题容器的类型（`TOPIC_ATTACHED` 或 `TOPIC_DETACHED`）。"""
        return self.getAttribute(const.ATTR_TYPE)

    def getSubTopics(self) -> list["TopicElement"]:
        """列出当前容器下的全部子主题。"""
        topics = []
        ownerWorkbook = self.getOwnerWorkbook()
        for t in self.getChildNodesByTagName(const.TAG_TOPIC):
            topics.append(TopicElement(t, ownerWorkbook))

        return topics

    def getSubTopicByIndex(self, index: int):
        """按索引获取指定子主题；索引越界时返回完整子主题列表。"""
        sub_topics = self.getSubTopics()
        if index < 0 or index >= len(sub_topics):
            return sub_topics

        return sub_topics[index]
