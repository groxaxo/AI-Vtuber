@echo off
chcp 65001

Miniconda3\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Miniconda3\python.exe -m pip install -r requirements.txt -i https://pypi.python.org/simple/

echo If everything succeeded, great. If there are failures, please install them manually.
cmd /k