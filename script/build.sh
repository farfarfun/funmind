#!/usr/bin/env bash
set -euo pipefail

# 构建、版本递增、安装校验、发布统一走 funbuild，不再手写 setup.py/twine 流程。
# Git 提交/推送需显式执行，不由本脚本隐式完成。
uv run funbuild build --multi
