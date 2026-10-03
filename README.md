# funmind

XMind 思维导图文件（`.xmind`）读写 SDK：基于 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 二次打包，支持用 Python 创建、解析、修改 `.xmind` 工作簿（workbook / sheet / topic），包括子主题、分离主题、标记（marker）、批注（comment）、超链接、关系线等元素。目前仅有本体代码和示例脚本，尚无独立文档站点或发布计划。

包名/导入名与仓库名一致，均为 `funmind`。经查 PyPI（`pypi.org/pypi/funmind/json`）返回 404，**目前并未实际发布到 PyPI**，只能本地安装使用。

## 安装

尚未发布到 PyPI，可克隆本仓库后用 [uv](https://docs.astral.sh/uv/) 本地安装：

```bash
git clone https://github.com/farfarfun/funmind.git
cd funmind
uv sync          # 安装依赖（含开发依赖）到本地虚拟环境
uv run pytest    # 运行测试
uv build         # 构建 wheel / sdist
```

也可以不使用 `uv`，直接用 pip 安装：

```bash
pip install .
```

## 用法示例

### 创建 XMind 文件

```python
import funmind.xmind as xmind
from funmind.xmind.core.markerref import MarkerId

workbook = xmind.load("my.xmind")  # 文件不存在则新建
sheet1 = workbook.get_primary_sheet()
sheet1.set_title("first sheet")

root_topic1 = sheet1.get_root_topic()
root_topic1.set_title("root node")
sub_topic1 = root_topic1.add_sub_topic()
sub_topic1.set_title("first sub topic")

xmind.save(workbook, path="test.xmind")
```

### 解析 XMind 文件

```python
from funmind import xmind

workbook = xmind.load("demo.xmind")
print(workbook.to_prettify_json())

sheet = workbook.get_primary_sheet()
root_topic = sheet.get_root_topic()
for topic in root_topic.get_sub_topics() or []:
    print(topic.get_title())
```

### 修改已有 XMind 文件

```python
from funmind import xmind
from funmind.xmind.core.markerref import MarkerId

workbook = xmind.load("demo.xmind")
root_topic = workbook.get_primary_sheet().get_root_topic()
root_topic.add_marker(MarkerId.starRed)

# 保存为新文件（推荐），或不传 path 直接覆盖原文件
xmind.save(workbook, path="xmind_update_demo.xmind")
```

更多示例见 `example/xmind/`（`create_xmind.py`、`parse_xmind.py`、`update_xmind.py`）。

本项目基于 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 二次打包，上游项目采用 MIT 协议开源，保留其原始版权声明。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
