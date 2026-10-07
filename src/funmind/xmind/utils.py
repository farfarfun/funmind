import os
import random
import re
import tempfile
import time
import zipfile
import warnings
from contextvars import ContextVar
from functools import wraps
from hashlib import md5

from xml.dom.minidom import parse, parseString

_CAMEL_CASE_RE = re.compile(r'([a-z0-9])([A-Z])')
_SNAKE_CASE_CALL = ContextVar("funmind_snake_case_call", default=False)


def _to_snake_case(name: str) -> str:
    """将驼峰名称转换为 snake_case，并保留缩写词的完整性。"""
    name = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return _CAMEL_CASE_RE.sub(r'\1_\2', name).lower()

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
def extract(path: str) -> zipfile.ZipFile:
    """以只读模式打开指定路径的 zip 压缩包。"""
    return zipfile.ZipFile(path, "r")


def compress(path: str) -> zipfile.ZipFile:
    """以写模式打开（新建）指定路径的 zip 压缩包。"""
    return zipfile.ZipFile(path, "w")


# ********** Path **********
join_path = os.path.join
split_ext = os.path.splitext


def get_abs_path(path: str) -> str:
    """返回文件的绝对路径。

    若 `path` 包含起始点（如 Unix 下的 ``/``），则使用该起始点而非当前工作目录；
    起始路径允许以 ``~`` 开头，会被替换为用户主目录。
    """

    fp, fn = os.path.split(path)
    if not fp:
        fp = os.getcwd()

    fp = os.path.abspath(os.path.expanduser(fp))

    return join_path(fp, fn)


# ********** Time **********
def get_current_time() -> int:
    """返回当前时间的毫秒级时间戳。"""
    return int(round(time.time() * 1000))


def readable_time(timestamp: int | str) -> str:
    """将毫秒级时间戳转换为可读的时间字符串（Python 内部按秒处理时间，故先转换为秒）。"""
    timestampe_in_seconds = float(timestamp) / 1000
    return time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(timestampe_in_seconds))


# ********** DOM **********

parse_dom = parse
parse_dom_string = parseString


# ********** Decorator **********

def prevent(func):
    """装饰 `func`，用于阻止被装饰函数在出错时向外抛出异常。

    目前项目内暂无调用方，仅捕获 `Exception`（而非 `BaseException`），
    以避免吞掉 `KeyboardInterrupt`/`SystemExit` 等控制流信号。
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def add_snake_case_aliases(cls: type) -> type:
    """为 cls 上驼峰命名的公开方法添加 snake_case 入口并弃用旧接口。

    本项目二次打包自上游 xmind 库，公开 API 大量沿用 Java/JS 风格的驼峰命名，
    与 SPEC.md 要求的 snake_case 命名规范冲突。为避免破坏性改名导致下游代码断裂，
    这里保留旧接口以兼容下游代码，但每次调用会发出 ``DeprecationWarning``；
    请迁移到同名 snake_case 接口，旧接口将于 1.0 移除。
    """
    for name in list(vars(cls)):
        if name.startswith('_'):
            continue
        snake = _to_snake_case(name)
        if snake == name:
            continue

        method = getattr(cls, name)
        if not callable(method):
            continue
        if not hasattr(cls, snake):
            @wraps(method)
            def snake_case_method(*args, __method=method, **kwargs):
                token = _SNAKE_CASE_CALL.set(True)
                try:
                    return __method(*args, **kwargs)
                finally:
                    _SNAKE_CASE_CALL.reset(token)

            setattr(cls, snake, snake_case_method)

        # 已手工标记弃用的方法无需再包一层，避免重复告警。
        if "已弃用" in (method.__doc__ or ""):
            continue

        @wraps(method)
        def deprecated_method(*args, __method=method, __name=name, __snake=snake, **kwargs):
            if not _SNAKE_CASE_CALL.get():
                warnings.warn(
                    f"{__name} 已弃用，请改用 {__snake}，将于 1.0 移除",
                    DeprecationWarning,
                    stacklevel=2,
                )
            return __method(*args, **kwargs)

        setattr(cls, name, deprecated_method)
    return cls


def check(attr: str):
    """返回一个方法装饰器：调用前检查 `self` 是否具有名为 `attr` 的属性，没有则直接返回 ``None``。"""

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, attr):
                return method(self, *args, **kwargs)

            return None

        return wrapper

    return decorator
