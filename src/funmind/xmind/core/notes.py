from . import const
from .mixin import TopicMixinElement


class NotesElement(TopicMixinElement):
    """表示主题备注的容器元素。"""
    TAG_NAME = const.TAG_NOTES

    def __init__(self, node=None, ownerTopic=None):
        super(NotesElement, self).__init__(node, ownerTopic)

    def getContent(self, format: str = const.PLAIN_FORMAT_NOTE) -> str | None:
        """返回指定格式的备注内容，默认返回纯文本备注。

        :param format: 备注格式，目前仅支持 `const.PLAIN_FORMAT_NOTE`（纯文本）。
        :raises NotImplementedError: 传入纯文本以外的格式时抛出。
        """

        _note = self.getFirstChildNodeByTagName(format)

        if not _note:
            return

        if format is const.PLAIN_FORMAT_NOTE:
            _note = PlainNotes(node=_note, ownerTopic=self.getOwnerTopic())
        else:
            raise NotImplementedError("Only support plain text notes right now, got format: %s" % format)

        return _note.getTextContent()


class _NoteContentElement(TopicMixinElement):
    def __init__(self, node=None, ownerTopic=None):
        super(_NoteContentElement, self).__init__(node, ownerTopic)

    def getFormat(self) -> str:
        """返回备注内容节点的标签名（即备注格式）。"""
        return self.getImplementation().tagName


class PlainNotes(_NoteContentElement):
    """纯文本备注。

    :param content: UTF-8 纯文本内容。
    :param node: `xml.dom.Element` 对象。
    :param ownerTopic: 所属的 `funmind.xmind.core.topic.TopicElement` 对象。
    """

    TAG_NAME = const.PLAIN_FORMAT_NOTE

    def __init__(self, content: str | None = None, node=None, ownerTopic=None) -> None:
        super(PlainNotes, self).__init__(node, ownerTopic)
        if content is not None:
            self.setTextContent(content)

    def setContent(self, content: str) -> None:
        """设置纯文本备注内容。"""
        self.setTextContent(content)
