# Stable Diffusion WebUI 部署报告

## 部署信息

| 项目 | 详情 |
|------|------|
| 部署日期 | 2026-05-08 |
| WebUI 版本 | AUTOMATIC1111 v1.10.1 |
| Python 版本 | 3.10.20 (Anaconda) |
| GPU | NVIDIA GeForce RTX 4060 (8GB) |
| CUDA 版本 | 12.1 |
| 模型路径 | ERNIE-Image_Turbo版 |
| 模型大小 | 12GB |

---

## 一、环境检查

### 1.1 系统环境

- **操作系统**: Windows 11 Home China 10.0.26200
- **Git**: 2.51.0.rc1.windows.1
- **Conda**: 4.5.11 (D:\ANA3)

### 1.2 Python 环境

系统存在多个 Python 版本：

| 路径 | 版本 |
|------|------|
| D:\Python\python.exe | 3.13.12 |
| D:\ANA3\python.exe | 3.7.0 |
| D:\ana1\python.exe | 3.12.7 |
| D:\ANA2\envs\yolov8\python.exe | 3.8.20 |
| **D:\ANA2\envs\sdwebui\python.exe** | **3.10.20** ✓ |

最终选择已存在的 `sdwebui` conda 环境（Python 3.10.20），符合官方推荐版本。

### 1.3 GPU 环境

```
GPU: NVIDIA GeForce RTX 4060 Laptop GPU
Driver Version: 591.74
CUDA Version: 13.1 (Driver支持)
显存: 8188MiB
```

---

## 二、部署过程

### 2.1 克隆 WebUI 仓库

```bash
cd c:/Users/dwqjdh/Desktop/AI_test/test7
git clone --depth=1 https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
```

克隆成功，仓库大小约 128MB。

### 2.2 配置 Python 环境

发现 `sdwebui` 环境已安装 torch 2.7.1+cpu（CPU版本），需要卸载：

```bash
D:/ANA2/envs/sdwebui/python.exe -m pip uninstall -y torch torchvision torchaudio
```

WebUI 启动时会自动安装 CUDA 版本的 torch。

### 2.3 配置启动参数

创建 `webui-user.bat` 配置文件：

```batch
@echo off
cd /d "%~dp0"

set PYTHON=D:\ANA2\envs\sdwebui\python.exe
set GIT=
set VENV_DIR=-
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set HF_ENDPOINT=https://hf-mirror.com

set STABLE_DIFFUSION_REPO=https://github.com/joypaul162/Stability-AI-stablediffusion.git
set STABLE_DIFFUSION_COMMIT_HASH=f16630a927e00098b524d687640719e4eb469b76

set COMMANDLINE_ARGS=--xformers --medvram-sdxl --autolaunch --theme dark --ckpt-dir "D:\迅雷下载"

call webui.bat
```

**关键配置说明**：

| 参数 | 说明 |
|------|------|
| `VENV_DIR=-` | 跳过创建新 venv，使用现有 conda 环境 |
| `PIP_INDEX_URL` | 清华镜像加速 pip 安装 |
| `HF_ENDPOINT` | HuggingFace 镜像加速模型下载 |
| `STABLE_DIFFUSION_REPO` | 替换为社区维护的 fork（原仓库已删除） |
| `--ckpt-dir` | 直接指定模型目录，无需移动 12GB 文件 |
| `--xformers` | GPU 内存优化 |
| `--medvram-sdxl` | 8GB 显存优化模式 |

---

## 三、遇到的问题及解决方案

### 3.1 问题一：Stability-AI/stablediffusion 仓库已删除

**现象**：
```
fatal: repository 'https://github.com/Stability-AI/stablediffusion.git/' not found
```

**原因**：官方仓库已被删除或迁移。

**解决方案**：
使用社区验证有效的 fork 仓库：
```bash
set STABLE_DIFFUSION_REPO=https://github.com/joypaul162/Stability-AI-stablediffusion.git
set STABLE_DIFFUSION_COMMIT_HASH=f16630a927e00098b524d687640719e4eb469b76
```

参考：GitHub Issue #17204

### 3.2 问题二：GitHub 克隆网络不稳定

**现象**：
```
error: RPC failed; HTTP 502 curl 22 The requested URL returned error: 502
fatal: expected 'packfile'
```

**解决方案**：
对于 `generative-models` 仓库，采用 ZIP 下载方式：

```bash
curl -L -o generative-models.zip "https://ghproxy.net/https://github.com/Stability-AI/generative-models/archive/45c443b316737a4ab6e40413d7794a7f5657c19f.zip"
unzip generative-models.zip
mv generative-models-45c443b3... generative-models
```

### 3.3 问题三：代码修改 - 跳过 commit hash 检查

由于通过 ZIP 下载的仓库没有 git 历史，需要修改 `modules/launch_utils.py`：

**原代码（第174-176行）**：
```python
if os.path.exists(dir):
    if commithash is None:
        return
```

**修改为**：
```python
if os.path.exists(dir):
    if not commithash:
        return
```

这样当 `commithash` 为空字符串时也能跳过检查。

### 3.4 问题四：缺少 dctorch 模块

**现象**：
```
ModuleNotFoundError: No module named 'dctorch'
```

**解决方案**：
```bash
D:/ANA2/envs/sdwebui/python.exe -m pip install dctorch
```

### 3.5 问题五：bat 文件行尾符问题

**现象**：Windows cmd 无法正确解析 LF 行尾的 bat 文件。

**解决方案**：使用 Python 生成 CRLF 格式的 bat 文件：
```python
content = '\\r\\n'.join(lines) + '\\r\\n'
with open('webui-user.bat', 'wb') as f:
    f.write(content.encode('gbk'))
```

---

## 四、最终启动

### 4.1 启动命令

```bash
cd c:/Users/dwqjdh/Desktop/AI_test/test7/stable-diffusion-webui
export VENV_DIR=-
export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
export HF_ENDPOINT="https://hf-mirror.com"
export STABLE_DIFFUSION_REPO="https://github.com/joypaul162/Stability-AI-stablediffusion.git"
export STABLE_DIFFUSION_COMMIT_HASH="f16630a927e00098b524d687640719e4eb469b76"
export STABLE_DIFFUSION_XL_COMMIT_HASH=""
export K_DIFFUSION_COMMIT_HASH=""
export BLIP_COMMIT_HASH=""
export ASSETS_COMMIT_HASH=""
export COMMANDLINE_ARGS="--xformers --medvram-sdxl --autolaunch --theme dark --ckpt-dir D:/迅雷下载"
D:/ANA2/envs/sdwebui/python.exe launch.py
```

### 4.2 启动成功日志

```
Python 3.10.20 | packaged by Anaconda, Inc. | (main, Mar 11 2026, 17:42:35) [MSC v.1942 64 bit (AMD64)]
Version: v1.10.1
Commit hash: 82a973c04367123ae98bd9abdf80d9eda9b910e2
Launching Web UI with arguments: --xformers --medvram-sdxl --autolaunch --theme dark --ckpt-dir 'D:/迅雷下载'
...
Running on local URL:  http://127.0.0.1:7860
Startup time: 59.8s
Model loaded in 358.4s
Applying attention optimization: xformers... done.
```

### 4.3 GPU 使用情况

启动后 GPU 显存占用：2761MiB / 8188MiB（约34%）

---

## 五、后续使用

### 5.1 日常启动方式

**方式一：命令行启动**
```bash
cd c:/Users/dwqjdh/Desktop/AI_test/test7/stable-diffusion-webui
D:/ANA2/envs/sdwebui/python.exe launch.py --xformers --medvram-sdxl --ckpt-dir "D:/迅雷下载"
```

**方式二：双击启动**
直接双击 `webui-user.bat` 文件。

### 5.2 WebUI 访问地址

- **本地地址**: http://127.0.0.1:7860
- **端口**: 7860（默认）

### 5.3 模型选择

在 WebUI 左侧 "Model" 标签页下拉菜单中选择：
- `白粉笔_Flxu_写实大模型_V1.0.safetensors`

---

## 六、已安装的依赖仓库

| 仓库 | 路径 | 用途 |
|------|------|------|
| stable-diffusion-stability-ai | repositories/stable-diffusion-stability-ai | SD 核心算法 |
| generative-models | repositories/generative-models | SDXL 支持 |
| k-diffusion | repositories/k-diffusion | K-diffusion 采样器 |
| BLIP | repositories/BLIP | 图像理解模型 |
| stable-diffusion-webui-assets | repositories/stable-diffusion-webui-assets | WebUI 资源文件 |

---

## 七、总结

### 7.1 关键成功因素

1. **使用现有 conda 环境**：避免了 Python 版本兼容性问题
2. **配置国内镜像**：大幅加速依赖下载
3. **使用社区 fork 仓库**：解决了官方仓库删除问题
4. **ZIP下载替代 git clone**：绕过网络不稳定问题
5. **--ckpt-dir 参数**：避免了12GB模型文件的复制/移动

### 7.2 部署耗时统计

| 阶段 | 耗时 |
|------|------|
| 仓库克隆 | ~2分钟 |
| 依赖仓库克隆/下载 | ~10分钟 |
| Python 依赖安装 | ~5分钟 |
| 首次模型加载 | ~6分钟 |
| WebUI 启动 | ~1分钟 |
| **总计** | **~25分钟** |

### 7.3 注意事项

1. 首次启动需要下载 CLIP、VAE 等基础模型，耗时较长
2. 8GB 显存建议使用 `--medvram-sdxl` 参数
3. 如遇网络问题，可使用 `HF_ENDPOINT=https://hf-mirror.com` 镜像

---

## 附录：文件结构

```
c:\Users\dwqjdh\Desktop\AI_test\test7\stable-diffusion-webui\
├── webui-user.bat          # 启动配置文件
├── launch.py               # 主启动脚本
├── modules\
│   └── launch_utils.py     # 已修改（commithash检查逻辑）
├── repositories\
│   ├── stable-diffusion-stability-ai\
│   ├── generative-models\
│   ├── k-diffusion\
│   ├── BLIP\
│   └── stable-diffusion-webui-assets\
├── models\
│   ├── Stable-diffusion\   # 空（模型在D:\迅雷下载）
│   ├── VAE\
│   ├── Lora\
│   └── ...
└── configs\
    └── v1-inference.yaml
```

---

**报告生成时间**: 2026-05-08
**生成工具**: Claude Code (claude-opus-4-7)