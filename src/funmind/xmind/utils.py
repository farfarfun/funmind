import os
import random
import re
import tempfile
import time
import zipfile
from functools import wraps
from hashlib import md5

from xml.dom.minidom import parse, parseString

_CAMEL_CASE_RE = re.compile(r'(?<!^)(?=[A-Z])')

# ********** Misc **********
temp_dir = tempfile.mkdtemp


def generate_id() -> str:
    """生成唯一的 26 位随机字符串。"""
    # 使用当前时间和随机数生成稳定长度的标识符。
    timestamp = md5(str(get_current_time()).encode('utf-8')).hexdigest()
    lotter = md5(str(random.random()).encode('utf-8')).hexdigest()
    _id = timestamp[19:] + lotter[:13]
    return _id


# ********** Zip **********
def extract(path):
    return zipfile.ZipFile(path, "r")


def compress(path):
    return zipfile.ZipFile(path, "w")


# ********** Path **********
join_path = os.path.join
split_ext = os.path.splitext


def get_abs_path(path):
    """
        Return the absolute path of a file

        If path contains a start point (eg Unix '/') then use the specified start point
        instead of the current working directory. The starting point of the file path is
        allowed to begin with a tilde "~", which will be replaced with the user's home directory.
    """

    fp, fn = os.path.split(path)
    if not fp:
        fp = os.getcwd()

    fp = os.path.abspath(os.path.expanduser(fp))

    return join_path(fp, fn)


# ********** Time **********
def get_current_time():
    """
    Get the current time in milliseconds
    """
    return int(round(time.time() * 1000))


def readable_time(timestamp):
    """
    Convert timestamp to human-readable time format

    Timestamp in milliseconds, convert to seconds
    Cause Python handle time in seconds
    """
    timestampe_in_seconds = float(timestamp) / 1000
    return time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(timestampe_in_seconds))


# ********** DOM **********

parse_dom = parse
parse_dom_string = parseString


# def create_document():
#     return dom.Document()
#
#
# def create_element(tagName, namespaceURI=None, prefix=None, localName=None):
#     return dom.Element(tagName, namespaceURI, prefix, localName)
#
#
# def load_XML(stream):
#     """
#         Create new Document while occure load XML error
#     """
#     try:
#         return dom.parse(stream)
#     except:
#         return create_document()


# ********** Decorator **********

def prevent(func):
    """
        Decorate func with this to prevent raising an Exception when
        an error is encountered

        目前项目内暂无调用方，仅捕获 `Exception`（而非 `BaseException`），
        以避免吞掉 `KeyboardInterrupt`/`SystemExit` 等控制流信号。
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def add_snake_case_aliases(cls):
    """为 cls 上驼峰命名的公开方法批量添加 snake_case 别名（委托原方法）。

    本项目二次打包自上游 xmind 库，公开 API 大量沿用 Java/JS 风格的驼峰命名，
    与 SPEC.md 要求的 snake_case 命名规范冲突。为避免破坏性改名导致下游代码断裂，
    这里仅追加委托别名，原驼峰方法继续保留、行为不变。
    """
    for name in list(vars(cls)):
        if name.startswith('_'):
            continue
        snake = _CAMEL_CASE_RE.sub('_', name).lower()
        if snake != name and not hasattr(cls, snake):
            setattr(cls, snake, getattr(cls, name))
    return cls


def check(attr):
    def decorator(method):
        """
            Decorate method with this to check whether the object
            has an attribute with the given name.
        """

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, attr):
                return method(self, *args, **kwargs)

            return None

        return wrapper

    return decorator
