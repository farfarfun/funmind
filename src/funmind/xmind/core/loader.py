import zipfile

from farlog import getLogger
from funmind.xmind.core.comments import CommentsBookDocument
from funmind.xmind.core.styles import StylesBookDocument

from . import const
from .workbook import WorkbookDocument
from .. import utils
from ..exceptions import InvalidXMindFileError

logger = getLogger(__name__)


class WorkbookLoader(object):
    def __init__(self, path: str) -> None:
        """加载指定路径的 XMind 工作簿。

        :param path: XMind 文件路径。文件不存在时视为新建工作簿，不会抛出异常；
            但文件存在且已损坏（非合法 zip 包）时会记录警告并同样按空工作簿处理。
        :raises InvalidXMindFileError: 当文件名缺少 `.xmind` 扩展名时抛出。
        """
        super(WorkbookLoader, self).__init__()
        self._input_source = utils.get_abs_path(path)

        file_name, ext = utils.split_ext(self._input_source)

        if ext != const.XMIND_EXT:
            raise InvalidXMindFileError(
                "The XMind filename is missing the '%s' extension: %s" % (const.XMIND_EXT, path)
            )

        # Input Stream
        self._content_stream = None
        self._styles_stream = None
        self._comments_steam = None

        try:
            with utils.extract(self._input_source) as input_stream:
                for stream in input_stream.namelist():
                    if stream == const.CONTENT_XML:
                        self._content_stream = utils.parse_dom_string(input_stream.read(stream))
                    elif stream == const.STYLES_XML:
                        self._styles_stream = utils.parse_dom_string(input_stream.read(stream))
                    elif stream == const.COMMENTS_XML:
                        self._comments_steam = utils.parse_dom_string(input_stream.read(stream))

        except FileNotFoundError:
            logger.debug("XMind 文件不存在，将创建新工作簿：{}", self._input_source)
        except (zipfile.BadZipFile, KeyError) as e:
            logger.warning("XMind 文件已损坏，按新工作簿处理：{}，原因：{}", self._input_source, e)

    def get_workbook(self):
        """ Parse XMind file to `WorkbookDocument` object and return
        """
        path = self._input_source
        content = self._content_stream
        styles = self._styles_stream
        comments = self._comments_steam
        stylesbook = StylesBookDocument(node=styles, path=path)
        commentsbook = CommentsBookDocument(node=comments, path=path)
        workbook = WorkbookDocument(node=content, path=path, stylesbook=stylesbook, commentsbook=commentsbook)

        return workbook

    def get_stylesbook(self):
        """ Parse Xmind styles.xml to `StylesBookDocument` object and return
        """
        content = self._styles_stream
        path = self._input_source

        stylesbook = StylesBookDocument(node=content, path=path)
        return stylesbook

    def get_commentsbook(self):
        content = self._comments_steam
        path = self._input_source

        commentsbook = CommentsBookDocument(node=content, path=path)
        return commentsbook
