import codecs
import os
import zipfile

from farlog import getLogger

from . import const
from .. import utils
from ..exceptions import InvalidXMindFileError

logger = getLogger(__name__)


class WorkbookSaver(object):
    def __init__(self, workbook) -> None:
        """将 `WorkbookDocument` 保存为 XMind 文件。

        :param workbook: `WorkbookDocument` 对象。
        """
        self._workbook = workbook
        self._temp_dir = utils.temp_dir()

    def _get_content_xml(self) -> str:
        content_path = utils.join_path(self._temp_dir, const.CONTENT_XML)
        # encoding 指定写文件时使用的编码。
        with codecs.open(content_path, "w", encoding="utf-8") as f:
            self._workbook.output(f)

        return content_path

    def _get_comments_xml(self) -> str:
        comments_path = utils.join_path(self._temp_dir, const.COMMENTS_XML)
        with codecs.open(comments_path, "w", encoding="utf-8") as f:
            self._workbook.commentsbook.output(f)

        return comments_path

    def _get_styles_xml(self) -> str:
        styles_path = utils.join_path(self._temp_dir, const.STYLES_XML)
        with codecs.open(styles_path, "w", encoding="utf-8") as f:
            self._workbook.stylesbook.output(f)

        return styles_path

    def _get_reference(self, except_revisions: bool = False) -> str:
        """从原 XMind 压缩包中解出附件引用（除 content/styles/comments 外的全部成员）。

        :param except_revisions: 是否跳过 `Revisions` 目录下的内容以节省空间。
        :return: 解压后的临时目录路径。
        """
        original_xmind_file = self._workbook.get_path()
        reference_dir = utils.temp_dir()
        reference_dir_abs = os.path.abspath(reference_dir)

        filename, suffix = utils.split_ext(original_xmind_file)
        if suffix != const.XMIND_EXT:
            raise InvalidXMindFileError(
                f'XMind 文件 "{original_xmind_file}" 必须使用 "{const.XMIND_EXT}" 扩展名'
            )

        original_zip = utils.extract(original_xmind_file)
        try:
            with original_zip as input_stream:
                for name in input_stream.namelist():
                    if name in [const.CONTENT_XML, const.STYLES_XML, const.COMMENTS_XML]:
                        continue
                    if const.REVISIONS_DIR in name and except_revisions:
                        continue
                    # 安全校验：拒绝绝对路径成员名，并确保解压目标始终落在
                    # reference_dir 内部，防止压缩包用 "../" 之类的成员名逃逸到
                    # 临时目录之外（zip slip / 路径穿越）。
                    if os.path.isabs(name):
                        logger.warning(
                            "跳过不安全的压缩包成员（绝对路径）：{}，来源：{}", name, original_xmind_file
                        )
                        continue
                    target_file = os.path.abspath(utils.join_path(reference_dir, name))
                    if target_file != reference_dir_abs and not target_file.startswith(
                        reference_dir_abs + os.sep
                    ):
                        logger.warning(
                            "跳过不安全的压缩包成员（路径穿越）：{}，来源：{}", name, original_xmind_file
                        )
                        continue
                    if not os.path.exists(os.path.dirname(target_file)):
                        os.makedirs(os.path.dirname(target_file))
                    with open(target_file, 'xb') as f:
                        f.write(original_zip.read(name))
        except (FileNotFoundError, zipfile.BadZipFile, KeyError) as e:
            logger.warning("读取附件引用失败，已跳过：{}，原因：{}", original_xmind_file, e)

        return reference_dir

    def save(
        self,
        path: str | None = None,
        only_content: bool = False,
        except_attachments: bool = False,
        except_revisions: bool = False,
    ) -> None:
        """将工作簿保存为 `.xmind` 文件；不传 `path` 则保存到工作簿自身记录的路径。

        :param path: 保存目标路径。
        :param except_revisions: 是否跳过 `Revisions` 内容以节省空间。
        :param except_attachments: 是否只保存 content.xml、comments.xml、styles.xml（不含附件）。
        :param only_content: 是否只保存 content.xml。
        """
        original_path = self._workbook.get_path()
        new_path = path or original_path

        new_path = utils.get_abs_path(new_path)
        new_filename, new_suffix = utils.split_ext(new_path)
        if new_suffix != const.XMIND_EXT:
            raise InvalidXMindFileError(
                f'XMind 文件 "{new_path}" 必须使用 "{const.XMIND_EXT}" 扩展名'
            )

        content = self._get_content_xml()
        if not only_content:
            styles = self._get_styles_xml()
            comments = self._get_comments_xml()
            if not except_attachments and os.path.exists(original_path):
                is_have_attachments = True
                reference_dir = self._get_reference(except_revisions)
            else:
                is_have_attachments = False

        f = utils.compress(new_path)
        f.write(content, const.CONTENT_XML)
        if not only_content:
            f.write(styles, const.STYLES_XML)
            f.write(comments, const.COMMENTS_XML)
            if not except_attachments and is_have_attachments:
                length = reference_dir.__len__()  # the length of the file string
                for dirpath, dirnames, filenames in os.walk(reference_dir):
                    for filename in filenames:
                        f.write(utils.join_path(dirpath, filename),
                                utils.join_path(dirpath[length + 1:] + os.sep, filename))
        f.close()
