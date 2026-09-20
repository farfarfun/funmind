# Changelog

## Unreleased

### 新增

- 补充真实单元测试（加载/保存/异常路径/snake_case 别名），替代此前的纯 import 冒烟测试。
- 为公开方法追加 snake_case 别名（委托原驼峰方法），兼容 SPEC.md 命名规范要求。
- 为核心异常路径引入 `InvalidXMindFileError`/`WorkbookError` 等领域异常，替代裸 `Exception`。

### 修复

- `loader.py`/`saver.py` 不再用 `except BaseException: pass` 静默吞掉所有异常，改为仅捕获预期的
  `FileNotFoundError`/`zipfile.BadZipFile`/`KeyError` 并记录日志，其余异常正常抛出。
- 修复 `core/__init__.py` 中 `DOM.Cell.TEXT_NODE`（不存在的属性）应为 `DOM.Node.TEXT_NODE` 的笔误，
  此前会导致任何读取文本内容（如 `getTitle()`）的调用抛出 `AttributeError`。

### 变更

- `script/build.sh` 改为统一走 `funbuild`，移除历史遗留的 `setup.py`/`twine` 流程与隐式
  `git commit && push`/`clear_history` 强制推送逻辑。

### Breaking

- Renamed the package from `notemind` to `funmind` to match the repository name (`note*` → `fun*` cleanup, part of farfarfun/todo-list#298). The import name and the PyPI package name declared in `pyproject.toml` both changed:
  - `import notemind...` -> `import funmind...`
  - PyPI package name `notemind` -> `funmind`
  - Checked `pip index versions notemind`: no distribution was ever published under the old name, so there is nothing to forward. If that changes, publishing a final forwarding release of `notemind` that points users to `funmind` is a manual follow-up for the repo owner, not automated here.
