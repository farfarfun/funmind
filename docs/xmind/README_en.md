> **说明**：本文件是上游项目 [zhuifengshen/xmind](https://github.com/zhuifengshen/xmind) 的原始
> README，仅作为版权与历史出处存档保留，其中的安装/用法说明（`pip3 install xmind`、
> `import xmind` 等）针对的是**上游包**，不适用于本仓库 `funmind`。
> `funmind` 的安装与用法请参见仓库根目录的 [README.md](../../README.md)。

# XMind

**XMind** is a a one-stop solution for creating, parsing, and updating XMind files. 
To help Python developers to easily work with XMind files and build XMind extensions.

## Install

Clone the repository to a local working directory
```
git clone git@github.com:zhuifengshen/xmind.git
```
	
Now there will be a directory named `xmind` under the current directory. Change to the directory `xmind-sdk-python` and install **XMind**.
```
pip3 install xmind
```
	
*It is highly recommended to install __XMind__ under an isolated python environment using [pipenv](https://github.com/pypa/pipenv)*

## Usage

Open an existing XMind file or create a new XMind file and place it into a given path
```
import xmind
workbook = xmind.load(/path/to/file/)  # Requires '.xmind' extension
```
	
Save XMind file to a path.
If the path is not given then the API will save to the path set in the workbook.
```
xmind.save(workbook)
```
or:
```
xmind.save(workbook, /save/file/to/path)
```

	
## LICENSE
```
The MIT License (MIT)

Copyright (c) 2019 Devin https://zhangchuzhao.site
Copyright (c) 2013 XMind, Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```