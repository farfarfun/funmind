from . import const
from .mixin import WorkbookMixinElement


class PositionElement(WorkbookMixinElement):
    TAG_NAME = const.TAG_POSITION

    def __init__(self, node=None, ownerWorkbook=None):
        super(PositionElement, self).__init__(node, ownerWorkbook)

    # FIXME: These should be converted to getter/setters

    def getX(self) -> str | None:
        """返回主题自由定位的 X 坐标（字符串形式）。"""
        return self.getAttribute(const.ATTR_X)

    def getY(self) -> str | None:
        """返回主题自由定位的 Y 坐标（字符串形式）。"""
        return self.getAttribute(const.ATTR_Y)

    def setX(self, x: int) -> None:
        """设置主题自由定位的 X 坐标。"""
        self.setAttribute(const.ATTR_X, int(x))

    def setY(self, y: int) -> None:
        """设置主题自由定位的 Y 坐标。"""
        self.setAttribute(const.ATTR_Y, int(y))
