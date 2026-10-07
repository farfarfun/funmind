from . import const
from .mixin import TopicMixinElement


class LabelsElement(TopicMixinElement):
    """表示主题所包含的标签集合。"""
    TAG_NAME = const.TAG_LABELS

    def __init__(self, node=None, ownerTopic=None):
        super(LabelsElement, self).__init__(node, ownerTopic)


class LabelElement(TopicMixinElement):
    """表示主题上的单个文本标签。"""
    TAG_NAME = const.TAG_LABEL

    def __init__(self, content=None, node=None, ownerTopic=None):
        super(LabelElement, self).__init__(node, ownerTopic)
        if content is not None:
            self.setTextContent(content)

    def getLabel(self) -> str | None:
        """返回标签文本内容。"""
        return self.getTextContent()

    def setLabel(self, content: str) -> None:
        """设置标签文本内容。"""
        self.setTextContent(content)
