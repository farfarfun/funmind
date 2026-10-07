# Changelog

## [0.0.3] - 2026-10-07

### 新增

- 补充真实单元测试（加载/保存/异常路径/snake_case 别名），替代此前的纯 import 冒烟测试。
- 为历史驼峰方法提供 snake_case 公开入口，兼容 SPEC.md 命名规范要求。
- 为公开类补充中文用途说明；历史驼峰方法现统一发出 `DeprecationWarning`，请迁移到对应的
  snake_case 接口，旧接口将于 1.0 移除。
- 为核心异常路径引入 `InvalidXMindFileError`/`WorkbookError` 等领域异常，替代裸 `Exception`。
- 为 `src/funmind/xmind/` 全部核心模块（`core/__init__.py`、`mixin.py`、`topic.py`、`sheet.py`、
  `workbook.py`、`comments.py`、`notes.py`、`labels.py`、`markerref.py`、`position.py`、
  `relationship.py`、`styles.py`、`saver.py`、`loader.py`、`utils.py`）补全类型标注与中文 docstring。
- 新增 `tests/test_api_coverage.py`，覆盖此前缺少测试的批注、备注、标签、关系线、超链接、
  附件保存/排除、marker 替换语义，以及 zip 压缩包路径穿越的安全回归测试。

### 修复

- `loader.py`/`saver.py` 不再用 `except BaseException: pass` 静默吞掉所有异常，改为仅捕获预期的
  `FileNotFoundError`/`zipfile.BadZipFile`/`KeyError` 并记录日志，其余异常正常抛出。
- 修复 `core/__init__.py` 中 `DOM.Cell.TEXT_NODE`（不存在的属性）应为 `DOM.Node.TEXT_NODE` 的笔误，
  此前会导致任何读取文本内容（如 `getTitle()`）的调用抛出 `AttributeError`。
- **安全修复**：`saver.py::WorkbookSaver._get_reference` 存在 zip 路径穿越（zip slip）漏洞，恶意
  `.xmind` 压缩包内若包含绝对路径或 `../` 转义的成员名，解压时会写出到临时目录之外。现已校验并
  拒绝此类成员名，仅记录警告并跳过。
- 修复 `topic.py::getStructureClass` 缺少 `return`，调用方永远拿到 `None`。
- 修复 `workbook.py::WorkbookDocument.setModifiedTime()` 调用 `_workbook_element.setModifiedTime()`
  时未传参，而底层方法要求必传 `time` 参数，一旦被调用会直接抛 `TypeError`；现已改为可选参数，
  不传时使用当前时间。
- 修复 `styles.py::StylesBookElement.getStyleElements` 逻辑写反：此前仅在"未找到样式节点"的分支
  返回（固定返回空列表），"找到样式节点"的分支反而没有 `return`、隐式返回 `None`，导致已存在的
  样式永远读不到。
- 清理 `utils.py`/`core/__init__.py` 中引用不存在的 `dom` 模块的死代码（注释掉的
  `create_document`/`create_element`/`load_XML` 占位实现）。
- 重写 `example/xmind/parse_xmind.py`：原脚本 `import xmind`（上游包，未安装会直接报错）且使用
  Python 3.13 已移除的 `pipes` 模块，现改为 `import funmind.xmind` 与 snake_case API，并以
  `shlex.quote` 替代 `pipes.quote`。
- `pyproject.toml` 的 `description` 字段由占位文案 `"funmind"` 改为实际描述。
- `README.md` 安装说明改为优先使用 `uv sync`/`uv run`/`uv build`（保留 `pip install .` 作为备选）。
- `LICENSE` 补充上游 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 的原始版权声明
  （第三方声明小节），与 README 中"保留其原始版权声明"的描述保持一致。
- `docs/xmind/README_en.md` 顶部加说明，明确这是上游项目的历史 README 存档，其中的安装/用法
  不适用于本仓库，避免读者误用 `pip3 install xmind`/`import xmind`。

### 变更

- `script/build.sh` 改为统一走 `funbuild`，移除历史遗留的 `setup.py`/`twine` 流程与隐式
  `git commit && push`/`clear_history` 强制推送逻辑。

### 废弃

- `setTitle` / `addMarker` / `getPrimarySheet` 已弃用，请分别迁移到
  `set_title` / `add_marker` / `get_primary_sheet`；旧接口将于 1.0 移除。
- `notemind` 已更名为 `funmind`，以匹配仓库名称。迁移方式如下：
  - `import notemind...` -> `import funmind...`
  - PyPI package name `notemind` -> `funmind`
  - 当前未发现旧包已发布；如后续发现旧包存在，需由维护者发布迁移提示版本。
