from funmind.xmind.core import Document, const, Element


class StylesBookDocument(Document):
    """`StylesBookDocument` 是对应 XMind 样式文件（styles.xml）的核心对象。
    """

    def __init__(self, node=None, path: str | None = None) -> None:
        """构造新的 `StylesBookDocument` 对象。

        :param node: 传入 DOM 节点并解析为 `StylesBookDocument`；不传则新建一个空样式文档。
        :param path: 样式文件的保存路径。
        """
        super(StylesBookDocument, self).__init__(node)
        self._path = path
        _stylesbook_element = self.getFirstChildNodeByTagName(const.TAG_STYLESBOOK)

        self._stylesbook_element = StylesBookElement(_stylesbook_element, self)

        if not _stylesbook_element:
            self.appendChild(self._stylesbook_element)

        self.setVersion(const.VERSION)

    def getStylesbookElement(self) -> "StylesBookElement":
        """返回样式文档对应的根元素。"""
        return self._stylesbook_element

    def getStyleElements(self) -> list["StyleElement"]:
        """返回全部样式元素；没有样式节点时返回空列表。"""
        style_element_list = []
        stylesbook_element = self.getStylesbookElement()
        styles_element = stylesbook_element.getFirstChildNodeByTagName(const.TAG_STYLES)
        if styles_element:
            for style_element in styles_element.childNodes:
                style_element_list.append(StyleElement(style_element))

        return style_element_list


class StylesBookElement(Element):
    """`StylesBookElement` 是样式文档中唯一的根元素。
    """
    TAG_NAME = const.TAG_STYLESBOOK

    def __init__(self, node=None, ownerStylesBook=None) -> None:
        super(StylesBookElement, self).__init__(node)
        self._owner_stylesbook = ownerStylesBook
        self.registerOwnerStylesBook()

        # 初始化默认命名空间属性。
        namespace = (const.NAMESPACE, const.XMLNS_STYLE)
        attrs = [const.NS_FO, const.NS_SVG]
        for attr in attrs:
            self.setAttributeNS(namespace, attr)

    def registerOwnerStylesBook(self) -> None:
        if self._owner_stylesbook:
            self.setOwnerDocument(self._owner_stylesbook.getOwnerDocument())


class StyleElement(Element):
    """`StyleElement` 是样式文档中的单个样式元素。

    例如：
    <style id="4sfj39toumgj9tupqn113ck9kq" type="topic">
        <topic-properties shape-class="org.xmind.topicShape.ellipse"/>
    </style>
    """
    TAG_NAME = const.TAG_STYLE

    def __init__(self, node=None, ownerStylesBook=None) -> None:
        super(StyleElement, self).__init__(node)
        self._owner_stylesbook = ownerStylesBook
        self.registerOwnerStylesBook()

    def registerOwnerStylesBook(self) -> None:
        if self._owner_stylesbook:
            self.setOwnerDocument(self._owner_stylesbook.getOwnerDocument())

    def getID(self) -> str | None:
        """返回样式元素的 id。"""
        return self.getAttribute(const.ATTR_ID)

    def getTopicStylePropertyByName(self, attr_name: str) -> str:
        """返回样式元素下 ``topic-properties`` 子节点的指定属性值。

        :param attr_name: 属性名，如 `const.ATTR_SHAPE_CLASS` 或 `const.ATTR_LINE_CLASS`。
        :return: 属性值；属性不存在时返回空字符串。
        """
        topic_properties_element = self.getFirstChildNodeByTagName(const.TAG_TOPIC_PROPERTIES)
        if not topic_properties_element.hasAttribute(attr_name):
            return ''
        return topic_properties_element.getAttribute(attr_name)
