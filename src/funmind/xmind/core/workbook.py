import json
import warnings

from . import Document
from . import const
from .mixin import WorkbookMixinElement
from .relationship import RelationshipElement
from .sheet import SheetElement
from .topic import TopicElement
from .. import utils
from ..exceptions import WorkbookError


class WorkbookElement(WorkbookMixinElement):
    """`WorkbookElement` 是文档中唯一的根元素，对应 XMind 内容文件的根节点。
    """
    TAG_NAME = const.TAG_WORKBOOK

    def __init__(self, node=None, ownerWorkbook=None):
        super(WorkbookElement, self).__init__(node, ownerWorkbook)

        # 初始化默认命名空间属性。
        namespace = (const.NAMESPACE, const.XMLNS_CONTENT)
        attrs = [const.NS_FO, const.NS_XHTML, const.NS_XLINK, const.NS_SVG]

        for attr in attrs:
            self.setAttributeNS(namespace, attr)

        # 工作簿至少需要包含一个工作表。
        if not self.getSheets():
            sheet = self.createSheet()
            self.addSheet(sheet)

    def setOwnerWorkbook(self, workbook):
        """`WorkbookElement` 只能归属一个 `WorkbookDocument`，禁止重新赋值。"""
        raise WorkbookError("WorkbookDocument allowed only contains one WorkbookElement")

    def getSheets(self) -> list[SheetElement]:
        """返回工作簿下的全部工作表。"""
        sheets = self.getChildNodesByTagName(const.TAG_SHEET)
        owner_workbook = self.getOwnerWorkbook()
        sheets = [SheetElement(sheet, owner_workbook) for sheet in sheets]

        return sheets

    def getSheetByIndex(self, index: int) -> SheetElement | None:
        """按索引获取工作表，索引越界时返回 ``None``。"""
        sheets = self.getSheets()

        if index < 0 or index >= len(sheets):
            return

        return sheets[index]

    def createSheet(self) -> SheetElement:
        """创建一个新的工作表（尚未添加到工作簿）。"""
        sheet = SheetElement(None, self.getOwnerWorkbook())
        return sheet

    def addSheet(self, sheet: SheetElement, index: int = -1) -> None:
        """将工作表添加到工作簿；索引越界时追加到末尾，否则插入到该索引之前。"""
        sheets = self.getSheets()
        if index < 0 or index >= len(sheets):
            self.appendChild(sheet)
        else:
            self.insertBefore(sheet, sheets[index])

        self.updateModifiedTime()

    def removeSheet(self, sheet: SheetElement) -> None:
        """从工作簿中移除工作表；工作簿至少需保留一个工作表，不足时不会移除。"""
        sheets = self.getSheets()
        if len(sheets) <= 1:
            return

        if sheet.getParentNode() == self.getImplementation():
            self.removeChild(sheet)
            self.updateModifiedTime()

    def moveSheet(self, original_index: int, target_index: int) -> None:
        """将工作表从原索引移动到目标索引。"""
        if original_index < 0 or original_index == target_index:
            return

        sheets = self.getSheets()
        if original_index >= len(sheets):
            return

        sheet = sheets[original_index]
        if not target_index < 0 and target_index < len(sheets) - 1:
            if original_index < target_index:
                target_index += 1
            else:
                target_index = target_index

            target = sheets[target_index]
            if target != sheet:
                self.removeChild(sheet)
                self.insertBefore(sheet, target)
        else:  # target < 0 or target >= len(sheets)
            self.removeChild(sheet)
            self.appendChild(sheet)

        self.updateModifiedTime()

    def getVersion(self) -> str | None:
        """返回工作簿格式版本号。"""
        return self.getAttribute(const.ATTR_VERSION)


utils.add_snake_case_aliases(WorkbookElement)


class WorkbookDocument(Document):
    """`WorkbookDocument` 是对应 XMind 工作簿的核心对象。
    """

    def __init__(self, node=None, path: str | None = None, stylesbook=None, commentsbook=None) -> None:
        """构造新的 `WorkbookDocument` 对象。

        :param node: 传入 DOM 节点并解析为 `WorkbookDocument`；不传则新建一个空工作簿。
        :param path: 工作簿的保存路径。
        :param stylesbook: 封装 XMind styles.xml 的 `StylesBookDocument` 实例。
        :param commentsbook: 封装 XMind comments.xml 的 `CommentsBookDocument` 实例。
        """
        super(WorkbookDocument, self).__init__(node)
        self._path = path
        self.stylesbook = stylesbook
        self.commentsbook = commentsbook
        # 确保工作簿内有且仅有一个 WorkbookElement 作为根节点。
        _workbook_element = self.getFirstChildNodeByTagName(const.TAG_WORKBOOK)

        self._workbook_element = WorkbookElement(_workbook_element, self)

        if not _workbook_element:
            self.appendChild(self._workbook_element)

        self.setVersion(const.VERSION)

    def getWorkbookElement(self) -> WorkbookElement:
        """返回工作簿对应的根元素 `WorkbookElement`。"""
        return self._workbook_element

    def createRelationship(
        self, topic1: TopicElement, topic2: TopicElement, title: str | None = None
    ) -> RelationshipElement:
        """在同一工作表下的两个主题之间创建关系线。

        :param topic1: 起点主题。
        :param topic2: 终点主题。
        :param title: 关系线标题，默认为空。
        :return: 新建的 `RelationshipElement` 实例。
        :raises WorkbookError: 当两个主题不属于同一工作表时抛出。
        """
        sheet1 = topic1.getOwnerSheet()
        sheet2 = topic2.getOwnerSheet()

        if sheet1.getImplementation() == sheet2.getImplementation():
            rel = sheet1.createRelationship(topic1.getID(), topic2.getID(), title)
            return rel
        else:
            raise WorkbookError("Topics not on the same sheet!")

    def createTopic(self) -> TopicElement:
        """创建一个新的 `TopicElement` 对象；该主题不会自动添加到工作簿中。"""
        return TopicElement(None, self)

    def getSheets(self) -> list[SheetElement]:
        """返回工作簿中的全部工作表，没有工作表时返回空列表。"""
        return self._workbook_element.getSheets()

    def get_primary_sheet(self) -> SheetElement:
        """返回工作簿中的第一个工作表。"""
        return self._workbook_element.getSheetByIndex(0)

    def getPrimarySheet(self) -> SheetElement:
        """兼容旧接口，请改用 :meth:`get_primary_sheet`。"""
        warnings.warn(
            "getPrimarySheet 已弃用，请改用 get_primary_sheet，将于 1.0 移除",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_primary_sheet()

    def createSheet(self, index: int = -1) -> SheetElement:
        """创建一个新工作表，并直接添加到工作簿中（无需再调用 `addSheet`）。

        :param index: 插入位置索引；不传或越界则追加到末尾。
        :return: 新建的 `SheetElement` 实例。
        """
        sheet = self._workbook_element.createSheet()
        self._workbook_element.addSheet(sheet, index)
        return sheet

    def removeSheet(self, sheet: SheetElement) -> None:
        """从工作簿中移除指定工作表。

        :param sheet: 待移除的 `SheetElement` 对象。
        """
        self._workbook_element.removeSheet(sheet)

    def moveSheet(self, original_index: int, target_index: int) -> None:
        """将工作表从原索引移动到目标索引。

        :param original_index: 待移动工作表的当前索引，须为合法的非负索引。
        :param target_index: 目标索引，须为合法的非负索引。
        """
        self._workbook_element.moveSheet(original_index, target_index)

    def getVersion(self) -> str | None:
        """返回工作簿格式版本号。"""
        return self._workbook_element.getVersion()

    def getModifiedTime(self) -> str | None:
        """返回工作簿最后修改时间的可读字符串，未设置时返回 ``None``。"""
        return self._workbook_element.getModifiedTime()

    def updateModifiedTime(self) -> WorkbookElement:
        """将工作簿最后修改时间刷新为当前时间。"""
        return self._workbook_element.updateModifiedTime()

    def setModifiedTime(self, time: int | None = None) -> None:
        """设置工作簿的最后修改时间戳。

        :param time: 毫秒级时间戳；不传则使用当前时间。
        """
        return self._workbook_element.setModifiedTime(time or utils.get_current_time())

    def get_path(self) -> str | None:
        """返回工作簿当前记录的绝对路径，未设置路径时返回 ``None``。"""
        if self._path:
            return utils.get_abs_path(self._path)

    def set_path(self, path: str) -> None:
        """设置工作簿的保存路径（内部会转换为绝对路径）。"""
        self._path = utils.get_abs_path(path)

    def getData(self) -> list[dict]:
        """以列表形式返回工作簿下所有工作表的数据。"""
        data = []
        for sheet in self.getSheets():
            data.append(sheet.getData())
        return data

    def to_prettify_json(self) -> str:
        """将工作簿内容转换为格式化的 JSON 字符串。"""
        return json.dumps(self.getData(), indent=4, separators=(',', ': '), ensure_ascii=False)


utils.add_snake_case_aliases(WorkbookDocument)
