# 《动手学深度学习》开发环境

这个目录按教材第 1 章“安装”的版本构建：Miniconda、名为 `d2l` 的 Python 3.9 环境、PyTorch 1.12.0、TorchVision 0.13.0、`d2l` 0.17.6 和 Jupyter Notebook。容器默认可在 CPU 上运行，适合前几章学习。

环境额外固定 `matplotlib-inline==0.1.7`、`traitlets==5.9.0` 和 `ipython==8.12.2`。前者解决 `d2l==0.17.6` 与 Matplotlib 3.5.1 的兼容问题；后两者解决 Notebook 6.4.12 在新版 Traitlets 下无法启动的问题。

## 用 VS Code 启动

1. 安装并启动 Docker Desktop。
2. 在 VS Code 中安装 **Dev Containers** 扩展。
3. 用 VS Code 单独打开本目录 `深度学习进阶`，而不是仓库的上一级目录。
4. 按 `Ctrl+Shift+P`，运行 **Dev Containers: Reopen in Container**。
5. 首次构建会下载镜像、Python 包和教材 Notebook；VS Code 随后会在容器中安装 Claude Code 与 Codex 扩展。完成后，右上角选择内核 **Python (d2l-pytorch)**，即可运行 `.ipynb` 文件。

容器创建完成时会自动执行一次环境自检。也可以在容器终端中手动运行：

```bash
python .devcontainer/verify_environment.py
```
如果没有下载d2l代码，运行：
```bash
bash .devcontainer/download_d2l_notebooks.sh
```
新开的 Bash 终端会自动进入 Conda 环境 `d2l`，提示符会以 `(d2l)` 开头。可用 `conda deactivate` 临时退出；关闭并重新打开终端后会再次自动进入。

可以用以下命令确认终端确实使用了教材环境：

```bash
which python
python --version
```

预期 Python 路径为 `/opt/conda/envs/d2l/bin/python`，版本为 Python 3.9。若当前终端仍指向 `/opt/conda/bin/python`，执行：

```bash
source /opt/conda/etc/profile.d/conda.sh
conda activate base
conda activate d2l
hash -r
```

然后运行完整自检：

```bash
python .devcontainer/verify_environment.py
```

也可以快速验证教材的 PyTorch API：

```bash
python -c "from d2l import torch as d2l; import torch; print(torch.__version__, torch.cuda.device_count())"
```

启动经典 Notebook：

```bash
jupyter notebook
```
运行后中断会出现类似：
```bash
 http://localhost:8888/?token=...
# 或
http://127.0.0.1:8888/?token=...
```
的链接，点击进入即可

当然也可以点击`d2l-zh/pytorch`的教材进入观看即可。

## 教材 Notebook

首次创建容器时会自动下载教材的中文 Notebook，预期位置是 `d2l-zh/pytorch`。下载脚本会检查该目录中确实存在 `.ipynb` 文件；下载失败或压缩包不包含 PyTorch 版时会明确报错。可以在容器终端中重试：

```bash
bash .devcontainer/download_d2l_notebooks.sh
```

不要使用 `d2l-zh/mxnet` 中的 Notebook 配合当前环境；这个容器安装的是 PyTorch，而不是 MXNet。

## 使用 NVIDIA GPU（可选）

先确认 Windows 已安装支持 WSL 2 的 NVIDIA 驱动，并在 Docker Desktop 中启用 WSL 2 后端。然后修改 `.devcontainer/devcontainer.json`：

1. 在 `runArgs` 中追加 `"--gpus=all"`。
2. 为教材锁定的 PyTorch 1.12.0 选择与驱动相容的 CUDA wheel，并相应调整 `environment.yml`。
3. 运行 **Dev Containers: Rebuild Container**。

重建后用下面的命令确认 GPU 已被识别：

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

如果只是学习前几章，CPU 环境已经足够；卷积网络等训练任务再启用 GPU 更合适。

## 文件和数据

- 当前打开的 `深度学习进阶` 目录会显式绑定挂载到容器的 `/workspaces/deep-learning-book`，Notebook 和代码会直接保存在 Windows 原目录中。
- 下载的数据缓存在工作区的 `data` 目录中；重建容器不会重复下载，并且可以直接在 Windows 中查看或备份。
- 共享内存设为 8 GB，避免多进程数据加载时常见的共享内存不足问题。
