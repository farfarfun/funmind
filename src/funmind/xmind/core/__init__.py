from xml.dom import minidom as DOM

from .. import utils


def create_document() -> DOM.Document:
    """构造一个新的 ``xml.dom.Document`` 对象。"""
    return DOM.Document()


def create_element(tag_name: str, namespaceURI: str | None = None, prefix: str | None = None,
                    localName: str | None = None) -> DOM.Element:
    """构造一个新的 ``xml.dom.Element`` 对象。"""
    element = DOM.Element(tag_name, namespaceURI, prefix, localName)
    return element


class Node(object):
    """XMind 工作簿所有组件的公共基类，封装对底层 `xml.dom` 节点的操作。
    """

    def __init__(self, node) -> None:
        # FIXME: 这里应当校验 node 是否为 dom.Node 的实例——
        # 后续 appendChild 会直接调用 self._node.appendChild，传入类型不对会直接抛异常。
        self._node = node

    def _equals(self, obj=None) -> bool:
        """比较传入对象与当前实例是否代表同一个 DOM 节点。"""
        if obj is None or not isinstance(obj, self.__class__):
            return False
        if obj == self:
            return True
        return self.getImplementation() == obj.getImplementation()

    def getImplementation(self):
        """返回底层 DOM 节点实现，用于直接操作 DOM。"""
        return self._node

    def getOwnerDocument(self):
        raise NotImplementedError("This method requires an implementation!")

    def setOwnerDocument(self, doc):
        raise NotImplementedError("This method requires an implementation!")

    def getLocalName(self, qualifiedName: str) -> str:
        """返回限定名（如 ``prefix:localName``）中的本地名部分。"""
        index = qualifiedName.find(":")
        if index >= 0:
            return qualifiedName[index + 1:]
        else:
            return qualifiedName

    def getPrefix(self, qualifiedName: str) -> str | None:
        """返回限定名中的前缀部分（含冒号），不含前缀时返回 ``None``。"""
        index = qualifiedName.find(":")
        if index >= 0:
            return qualifiedName[:index + 1]

    def appendChild(self, node: "Node"):
        """将传入节点追加到当前节点子节点列表末尾。"""
        node.setOwnerDocument(self.getOwnerDocument())

        node_impel = node.getImplementation()

        return self._node.appendChild(node_impel)

    def insertBefore(self, new_node: "Node", ref_node: "Node"):
        """将新节点插入到 `ref_node` 之前；`ref_node` 必须是当前节点的子节点。"""
        new_node.setOwnerDocument(self.getOwnerDocument())

        new_node_imple = new_node.getImplementation()
        ref_node_imple = ref_node.getImplementation()

        return self._node.insertBefore(new_node_imple, ref_node_imple)

    def getChildNodesByTagName(self, tag_name: str) -> list:
        """返回指定标签名的直接子节点列表（不递归查找所有后代）。"""
        child_nodes = []
        for node in self._node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue

            if node.tagName == tag_name:
                child_nodes.append(node)

        return child_nodes

    def getFirstChildNodeByTagName(self, tag_name: str):
        """返回指定标签名的第一个直接子节点，不存在时返回 ``None``。"""
        child_nodes = self.getChildNodesByTagName(tag_name)

        if len(child_nodes) >= 1:
            return child_nodes[0]

    def getParentNode(self):
        """返回父节点。"""
        return self._node.parentNode

    def _isOrphanNode(self, node) -> bool:
        if node is None:
            return True
        if node.nodeType == node.DOCUMENT_NODE:
            return False

        return self._isOrphanNode(node.parentNode)

    def isOrphanNode(self) -> bool:
        """判断当前节点是否未挂载到任何文档（孤立节点）。"""
        return self._isOrphanNode(self._node)

    def iterChildNodesByTagName(self, tag_name: str):
        """按标签名迭代当前节点的直接子节点。"""
        for node in self._node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue

            if node.tagName == tag_name:
                yield node

    def removeChild(self, child_node: "Node") -> None:
        """从当前节点移除指定子节点。"""
        child_node = child_node.getImplementation()
        self._node.removeChild(child_node)

    def output(self, output_stream) -> None:
        """将节点对应的 XML 内容写出到指定流。"""
        return self._node.writexml(output_stream, addindent="", newl="", encoding="utf-8")


class Document(Node):
    """对应 `xml.dom.Document` 的封装，XMind 各类 Book 文档的基类。
    """

    def __init__(self, node=None) -> None:
        # FIXME: 理论上应调用基类构造方法 super(Document, self).__init__()。
        self._node = node or self._documentConstructor()

    def _documentConstructor(self) -> DOM.Document:
        return DOM.Document()

    @property
    def documentElement(self):
        """返回底层 DOM 实现的根元素，供直接操作。"""
        return self._node.documentElement

    def getOwnerDocument(self):
        return self._node

    def createElement(self, tag_name: str):
        """创建一个新的 DOM 元素节点（尚未添加到文档树中）。"""
        return self._node.createElement(tag_name)

    def setVersion(self, version: str) -> None:
        """为根元素设置版本号属性（已存在则不覆盖）。"""
        element = self.documentElement
        if element and not element.hasAttribute("version"):
            element.setAttribute("version", version)

    def replaceVersion(self, version: str) -> None:
        """为根元素设置版本号属性（无条件覆盖）。"""
        element = self.documentElement
        if element:
            element.setAttribute("version", version)

    def getElementById(self, id: str):
        """按 id 查找元素，找不到时返回 ``None``。"""
        return self._node.getElementById(id)


class Element(Node):
    """对应 `xml.dom.Element` 的封装，XMind 各类文档元素的基类。
    """

    TAG_NAME = ""

    def __init__(self, node=None) -> None:
        # FIXME: 理论上应调用基类构造方法 super(Element, self).__init__()。
        self._node = node or self._elementConstructor(self.TAG_NAME)

    def _elementConstructor(self, tag_name: str, namespaceURI: str | None = None,
                             prefix: str | None = None, localName: str | None = None):
        return DOM.Element(tag_name,
                           namespaceURI,
                           self.getPrefix(tag_name),
                           self.getLocalName(tag_name))

    def getOwnerDocument(self):
        return self._node.ownerDocument

    def setOwnerDocument(self, doc_imple) -> None:
        self._node.ownerDocument = doc_imple

    def setAttributeNS(self, namespace: tuple[str, str], attr: tuple[str, str, str]) -> None:
        """为 DOM 实现设置带命名空间的属性。

        :param namespace: ``(命名空间名, 命名空间取值)`` 二元组。
        :param attr: ``(namespaceURI, localName, value)`` 三元组。
        """
        namespace_name, namespace_value = namespace
        if not self._node.hasAttribute(namespace_name):
            self._node.setAttribute(namespace_name, namespace_value)

        namespaceURI, localName, value = attr
        if not self._node.hasAttributeNS(namespaceURI, localName):
            qualifiedName = "%s:%s" % (namespace_name, localName)
            self._node.setAttributeNS(namespaceURI, qualifiedName, value)

    def getAttribute(self, attr_name: str) -> str | None:
        """
        Get attribute with specified name. And allowed get attribute with
        specified name in ``prefix:localName`` format.
        """
        if not self._node.hasAttribute(attr_name):
            localName = self.getLocalName(attr_name)
            if localName != attr_name:
                return self.getAttribute(localName)
            return

        return self._node.getAttribute(attr_name)

    def setAttribute(self, attr_name: str, attr_value=None) -> None:
        """设置元素属性；当 `attr_value` 为 ``None`` 且该属性已存在时，会删除该属性。"""
        if attr_value is not None:
            self._node.setAttribute(attr_name, str(attr_value))
        elif self._node.hasAttribute(attr_name):
            self._node.removeAttribute(attr_name)

    def createElement(self, tag_name: str) -> None:
        """创建新元素；创建后不会自动加入当前元素的子节点列表，
        需另外调用 `appendChild` 或 `insertBefore` 添加。

        注：当前实现为占位，未实际创建元素。
        """
        pass

    def addIdAttribute(self, attr_name: str) -> None:
        """若元素尚未设置 `attr_name` 属性，则生成一个随机 id 并设置为该属性。"""
        if not self._node.hasAttribute(attr_name):
            id = utils.generate_id()
            self._node.setAttribute(attr_name, id)

            if self.getOwnerDocument():
                self._node.setIdAttribute(attr_name)

    def getIndex(self) -> int:
        """返回当前元素在父节点子节点列表中的索引；没有父节点时返回 -1。"""
        parent = self.getParentNode()
        if parent:
            index = 0
            for node in parent.childNodes:
                if self._node is node:
                    return index
                index += 1

        return -1

    def getTextContent(self) -> str | None:
        """返回元素下全部文本子节点拼接后的内容，没有文本内容时返回 ``None``。"""
        text = []
        for node in self._node.childNodes:
            if node.nodeType == DOM.Node.TEXT_NODE:
                text.append(node.data)

        if not len(text) > 0:
            return

        text = "\n".join(text)
        return text

    def setTextContent(self, data: str) -> None:
        """将元素的文本内容替换为 `data`（会先清空已有文本子节点）。"""
        for node in self._node.childNodes:
            if node.nodeType == DOM.Node.TEXT_NODE:
                self._node.removeChild(node)

        text = DOM.Text()
        text.data = data

        self._node.appendChild(text)
