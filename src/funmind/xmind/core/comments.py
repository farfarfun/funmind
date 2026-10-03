#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
封装 XMind 批注文件 comments.xml 的读写。
"""
import random

from funmind.xmind import utils
from funmind.xmind.core import Document, const, Element


class CommentsBookDocument(Document):
    """`CommentsBookDocument` 是对应 XMind 批注文件（comments.xml）的核心对象。

    文件示例：
    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <comments version="2.0" xmlns="urn:xmind:xmap:xmlns:comments:2.0">
        <comment author="zhangchuzhao" object-id="75sr1n3r5aia1b7p15df4d77r6" time="1543655624230">
            <content>批注demo</content>
        </comment>
    </comments>
    """

    def __init__(self, node=None, path: str | None = None) -> None:
        """构造新的 `CommentsBookDocument` 对象。

        :param node: 传入 DOM 节点并解析为 `CommentsBookDocument`；不传则新建一个空批注文档。
        :param path: 工作簿的保存路径。
        """
        super(CommentsBookDocument, self).__init__(node)
        self._path = path

        _commentsbook_element = self.getFirstChildNodeByTagName(const.TAG_COMMENTSBOOK)
        self._commentsbook_element = CommentsBookElement(_commentsbook_element, self)

        if not _commentsbook_element:
            self.appendChild(self._commentsbook_element)

        self.setVersion(const.VERSION)

    def getCommentsBookElement(self) -> "CommentsBookElement":
        """返回批注文档对应的根元素。"""
        return self._commentsbook_element

    def getComments(self) -> list["CommentElement"]:
        """返回全部批注元素。"""
        return self._commentsbook_element.getComments()

    def addComment(self, content: str, topic_id: str, author: str | None = None) -> "CommentElement":
        """新增一条批注。

        :param content: 批注正文内容。
        :param topic_id: 被批注主题的 id（须为 26 位合法主题 id）。
        :param author: 批注作者，不传则记为 ``admin``。
        """
        return self._commentsbook_element.addComment(content, topic_id, author)

    def getComment(self, topic_id: str) -> str | None:
        """返回指定主题 id 对应的批注内容，没有则返回 ``None``。"""
        mapping = self.getData()
        if topic_id in mapping.keys():
            return mapping[topic_id]
        else:
            return None

    def getData(self) -> dict:
        """以 ``{主题id: 批注内容}`` 字典形式返回全部批注；同一主题多条批注以换行拼接。"""
        data = {}
        for comment in self.getComments():
            object_id = comment.getObjectId()
            content = comment.getContent()
            if object_id in data.keys():
                exist_content = data[object_id]
                data[object_id] = exist_content + '\n' + content
            else:
                data[object_id] = content
        return data


class CommentsBookElement(Element):
    """`CommentsBookElement` 是批注文档中唯一的根元素。

    文件示例：
    <comments version="2.0" xmlns="urn:xmind:xmap:xmlns:comments:2.0">
        <comment author="zhangchuzhao" object-id="75sr1n3r5aia1b7p15df4d77r6" time="1543655624230">
            <content>批注demo</content>
        </comment>
    </comments>
    """
    TAG_NAME = const.TAG_COMMENTSBOOK

    def __init__(self, node=None, ownerCommentsBook=None):
        super(CommentsBookElement, self).__init__(node)
        self._owner_commentsbook = ownerCommentsBook
        self.registerOwnerCommmentsBook()
        self.setAttribute(const.NAMESPACE, const.XMLNS_COMMENTS)

    def registerOwnerCommmentsBook(self) -> None:
        if self._owner_commentsbook:
            self.setOwnerDocument(self._owner_commentsbook.getOwnerDocument())

    def getOwnerCommentsBook(self):
        """返回所属的 `CommentsBookDocument`。"""
        return self._owner_commentsbook

    def getComments(self) -> list["CommentElement"]:
        """返回全部批注元素。"""
        comments = self.getChildNodesByTagName(const.TAG_COMMENT)
        owner_commentsbook = self.getOwnerCommentsBook()
        comments = [CommentElement(node=comment, ownerCommentsBook=owner_commentsbook) for comment in comments]
        return comments

    def addComment(self, content: str, topic_id: str, author: str | None = None) -> "CommentElement":
        """新增一条批注并追加到批注文档中。"""
        comment = CommentElement(content=content, node=None, ownerCommentsBook=self.getOwnerCommentsBook())
        comment.setObjectId(topic_id)
        comment.setAuthor(author)
        self.appendChild(comment)
        return comment


class CommentElement(Element):
    """`CommentElement` 是批注文档中的单条批注元素。

    文件示例：
    <comment author="zhangchuzhao" object-id="75sr1n3r5aia1b7p15df4d77r6" time="1543655624230">
        <content>批注demo</content>
    </comment>
    """
    TAG_NAME = const.TAG_COMMENT

    def __init__(self, content: str | None = None, node=None, ownerCommentsBook=None) -> None:
        super(CommentElement, self).__init__(node)
        self._owner_commentsbook = ownerCommentsBook
        self.registerOwnerCommentsbook()

        if not self.getAttribute(const.ATTR_TIME):
            # XMind 的已知缺陷：同一秒内生成的多条批注只会展示第一条，这里追加随机数加以规避。
            self.setAttribute(const.ATTR_TIME, int(utils.get_current_time()) + random.randint(1, 10))

        if content:
            self._content_element = ContentElement(content=content, ownerCommentsBook=ownerCommentsBook)
            self.appendChild(self._content_element)
        else:
            content_element = self.getFirstChildNodeByTagName(const.TAG_CONTENT)
            self._content_element = ContentElement(node=content_element, ownerCommentsBook=ownerCommentsBook)

    def registerOwnerCommentsbook(self) -> None:
        if self._owner_commentsbook:
            self.setOwnerDocument(self._owner_commentsbook.getOwnerDocument())

    def getObjectId(self) -> str | None:
        """返回批注所关联的主题 id。"""
        return self.getAttribute(const.ATTR_OBJECT_ID)

    def setObjectId(self, topipc_id: str) -> None:
        """设置批注所关联的主题 id（须为 26 位合法主题 id）。

        :raises ValueError: 当 `topipc_id` 为空或长度不是 26 时抛出。
        """
        if topipc_id and len(topipc_id) == 26:
            self.setAttribute(const.ATTR_OBJECT_ID, topipc_id)
        else:
            raise ValueError('Invalid comment object id: %s' % topipc_id)

    def getAuthor(self) -> str | None:
        """返回批注作者。"""
        return self.getAttribute(const.ATTR_AUTHOR)

    def setAuthor(self, author: str | None) -> None:
        """设置批注作者，不传则记为 ``admin``。"""
        if author:
            self.setAttribute(const.ATTR_AUTHOR, author)
        else:
            self.setAttribute(const.ATTR_AUTHOR, 'admin')

    def getContent(self) -> str | None:
        """返回批注正文内容。"""
        return self._content_element.getTextContent()

    def setContent(self, content: str) -> None:
        """设置批注正文内容。"""
        self._content_element.setTextContent(content)


class ContentElement(Element):
    """`ContentElement` 是批注元素下的正文子元素。

    文件示例：
    <comment author="zhangchuzhao" object-id="75sr1n3r5aia1b7p15df4d77r6" time="1543655624230">
        <content>批注demo</content>
    </comment>
    """
    TAG_NAME = const.TAG_CONTENT

    def __init__(self, content: str | None = None, node=None, ownerCommentsBook=None) -> None:
        super(ContentElement, self).__init__(node)
        self._owner_commentsbook = ownerCommentsBook
        if content:
            self.setTextContent(content)

    def getContent(self) -> str | None:
        """返回批注正文文本内容。"""
        return self.getTextContent()

    def setContent(self, content: str) -> None:
        """设置批注正文文本内容。"""
        self.setTextContent(content)
