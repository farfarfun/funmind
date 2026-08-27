# funmind

XMind 思维导图文件（`.xmind`）读写 SDK：基于 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 二次打包，支持用 Python 创建、解析、修改 `.xmind` 工作簿（workbook / sheet / topic），包括子主题、分离主题、标记（marker）、批注（comment）、超链接、关系线等元素。目前仅有本体代码和示例脚本，尚无独立文档站点或发布计划。

> **注意：仓库名与导入名不同。** 仓库名是 `funmind`，但实际 Python 包目录、`pyproject.toml` 声明的包名、以及历史上发布过的 PyPI 名都是 `notemind`（`note*` → `fun*` 改名时遗留未改）。`pip install` 和 `import` 都要用 `notemind`，不是 `funmind`。经查 PyPI（`pypi.org/pypi/notemind/json` 与 `pypi.org/pypi/funmind/json`）均返回 404，**目前并未实际发布到 PyPI**，只能本地安装使用。

## 安装

尚未发布到 PyPI，可克隆本仓库后本地安装：

```bash
git clone https://github.com/farfarfun/funmind.git
cd funmind
pip install .
```

## 用法示例

### 创建 XMind 文件

```python
import notemind.xmind as xmind
from notemind.xmind.core.markerref import MarkerId

workbook = xmind.load("my.xmind")  # 文件不存在则新建
sheet1 = workbook.getPrimarySheet()
sheet1.setTitle("first sheet")

root_topic1 = sheet1.getRootTopic()
root_topic1.setTitle("root node")
sub_topic1 = root_topic1.addSubTopic()
sub_topic1.setTitle("first sub topic")

xmind.save(workbook, path="test.xmind")
```

### 解析 XMind 文件

```python
from notemind import xmind

workbook = xmind.load("demo.xmind")
print(workbook.to_prettify_json())

sheet = workbook.getPrimarySheet()
root_topic = sheet.getRootTopic()
for topic in root_topic.getSubTopics() or []:
    print(topic.getTitle())
```

### 修改已有 XMind 文件

```python
from notemind import xmind
from notemind.xmind.core.markerref import MarkerId

workbook = xmind.load("demo.xmind")
root_topic = workbook.getPrimarySheet().getRootTopic()
root_topic.addMarker(MarkerId.starRed)

# 保存为新文件（推荐），或不传 path 直接覆盖原文件
xmind.save(workbook, path="xmind_update_demo.xmind")
```

更多示例见 `example/xmind/`（`create_xmind.py`、`parse_xmind.py`、`update_xmind.py`）。
