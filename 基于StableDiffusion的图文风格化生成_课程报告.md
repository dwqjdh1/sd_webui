# 基于 Stable Diffusion 的图文风格化生成系统

## 课程报告

---

## 一、项目概述

### 1.1 项目背景

面向创意设计、广告营销、游戏原画等领域，传统图像设计依赖专业设计师手工绘制，门槛高、周期长、成本高。本项目基于 **Stable Diffusion** 开源扩散模型，构建一套图文风格化生成系统，支持用户通过文字描述或上传参考图快速生成高质量风格化图像，并可通过姿态骨架、边缘图等条件实现精准控制，显著降低专业设计门槛。

### 1.2 核心目标

| 目标 | 说明 |
|------|------|
| 文生图/图生图 | 支持正向/负向提示词生成图像，支持重绘强度调节变换风格 |
| 可控生成 | 基于 ControlNet 实现姿态、边缘等条件控制 |
| 超分辨率修复 | 4 倍放大并修复细节 |
| 推理加速 | xformers + 半精度优化，单图生成 < 3 秒，显存占用 < 6GB |
| 提示词自动化 | BLIP 自动生成基础描述，叠加风格关键词 |
| LoRA 微调 | 小样本保持身份/风格一致性 |

### 1.3 运行环境

| 项目 | 详情 |
|------|------|
| 操作系统 | Windows 11 Home |
| GPU | NVIDIA GeForce RTX 4060 Laptop (8GB VRAM) |
| CUDA | 12.1 |
| Python | 3.10.20 (Anaconda) |
| PyTorch | 2.1.2+cu121 |
| WebUI | AUTOMATIC1111 v1.10.1 |
| 基础模型 | ERNIE-Image_Turbo版 |

---

## 二、系统架构

```
用户层
  ├── WebUI 可视化界面 (Gradio)
  ├── 提示词输入 / 图片上传
  └── 参数调节面板

服务层
  ├── 文生图 Pipeline (Stable Diffusion XL)
  ├── 图生图 Pipeline (Img2Img + Inpainting)
  ├── ControlNet 条件控制模块
  ├── Ultimate SD Upscale 超分辨率模块
  ├── LoRA 动态加载模块
  └── 提示词辅助 (Prompt All-in-One + 汉化)

模型层
  ├── Base Model: ERNIE-Image_Turbo版
  ├── ControlNet: OpenPose / Canny / Depth (Control-LoRA)
  ├── LoRA: 用户自定义风格/人物微调模型
  ├── VAE: 图像编解码器
  └── ESRGAN: 4x 超分模型

辅助层
  ├── BLIP 图像理解 (提示词反推)
  ├── 风格关键词库
  └── 推理优化: xformers + FP16 + 显存管理
```

---

## 三、基础功能实现

### 3.1 文生图 (Text-to-Image)

**功能描述**: 用户输入正向提示词（描述想要生成的内容）和负向提示词（排除不想要的元素），系统自动生成对应图像。

**实现方式**:
- 基于 AUTOMATIC1111 WebUI 的 txt2img 模块
- 使用 SDXL 基础模型，支持 1024x1024 原生分辨率
- 支持多种采样器（DPM++ 2M Karras、Euler a 等）
- 支持步数（Steps）、CFG Scale（提示词遵循度）调节

**典型参数配置**:
```
正向提示词: masterpiece, best quality, a beautiful girl in a garden, sunlight, realistic
负向提示词: lowres, bad anatomy, bad hands, text, error, missing fingers, blurry
采样器: DPM++ 2M Karras
步数: 30
CFG Scale: 7
分辨率: 1024 x 1024
```


### 3.3 ControlNet 可控生成

**功能描述**: 基于姿态骨架 (OpenPose) 或边缘图 (Canny) 等条件输入，精准控制生成图像的人物姿态、轮廓结构，使输出更贴近用户预期。

**已安装扩展**: `sd-webui-controlnet` (Mikubill)

**支持的控制类型**:

| 控制类型 | 输入条件 | 适用场景 |
|----------|----------|----------|
| OpenPose | 人体骨架关键点 | 控制人物姿态、动作 |
| Canny | 边缘检测图 | 控制整体轮廓、构图 |
| Depth | 深度图 | 控制空间层次、远近关系 |
| Scribble | 手绘草图 | 快速原型设计 |

**模型配置**:
- 模型存放路径: `stable-diffusion-webui/models/ControlNet/`
- 推荐 SDXL 轻量模型（适合 8GB 显存）:
  - `control-lora-openposeXL2-rank256.safetensors` (~140MB)
  - `control-lora-cannyXL-rank256.safetensors` (~140MB)

**使用流程**:
1. 上传参考图到 ControlNet 面板
2. 选择预处理器（如 `openpose_full` 或 `canny`）
3. 选择对应 ControlNet 模型
4. 设置控制权重 (Control Weight): 0.8 ~ 1.0
5. 输入提示词生成图像

### 3.4 超分辨率修复 (4x Upscale)

**功能描述**: 将低分辨率图像放大 4 倍，同时通过 AI 修复细节，避免传统插值的模糊问题。

**已安装扩展**: `ultimate-upscale-for-automatic1111`

**技术方案**:
- **ESRGAN 模型**: `ESRGAN_4x.pth`（已安装，16MB）
- **Ultimate SD Upscale**: 基于 Tile 分块 + SD 重绘的超分方案
  - 将大图切分为 512x512 小块逐一处理
  - 每个小块使用图生图进行细节重绘
  - 最后合并为 4 倍大图

**两种超分方式对比**:

| 方式 | 速度 | 显存占用 | 质量 | 适用场景 |
|------|------|----------|------|----------|
| ESRGAN 直接放大 | 快 | 低 | 中等 | 快速预览 |
| Ultimate SD Upscale | 慢 | 高 | 极高 | 成品输出 |

### 3.5 可视化界面与参数调节

**界面平台**: AUTOMATIC1111 WebUI (Gradio)

**访问地址**: `http://127.0.0.1:7860`

**可调节参数**:
- 采样器与步数
- 分辨率与批次数量
- CFG Scale（提示词强度）
- 种子值（可复现结果）
- 重绘强度（图生图）
- ControlNet 权重与起始/结束步数

---

## 四、优化方向实现

### 4.1 LoRA 微调：小样本保持身份一致性

**技术原理**: LoRA (Low-Rank Adaptation) 通过在原始模型权重旁路注入低秩矩阵进行微调，仅需数十张图片即可学习特定人物、物品或风格，冻结主模型参数，显存占用低、训练速度快。

**当前配置**:
- LoRA 模型目录: `stable-diffusion-webui/models/Lora/`（默认路径，与主模型分离避免混淆）
- WebUI 支持在提示词中通过 `<lora:模型名:权重>` 动态调用
- 若需使用 LoRA 模型，将 `.safetensors` 文件放入 `models/Lora/` 目录即可识别

**使用示例**:
```
正向提示词: a portrait of <lora:custom_character:0.8>, realistic, 8k
```

**训练流程（如需自行训练）**:
1. 准备 15-50 张目标人物/物品图片
2. 使用 WebUI 内置训练功能或 kohya_ss 工具
3. 设置学习率、训练轮数、LoRA 维度 (rank=64/128)
4. 训练完成后放入 `models/Lora/` 目录即可使用

### 4.2 推理加速：xformers + 半精度 + 显存优化

**目标**: 单图生成 < 3 秒，显存占用 < 6GB

**已启用优化措施**:

| 优化手段 | 配置参数 | 效果 |
|----------|----------|------|
| xformers 注意力优化 | `--xformers` | 减少 20-30% 显存占用，加速 10-15% |
| 半精度推理 (FP16) | 默认自动 | 显存减半，速度提升 |
| VAE 全精度保护 | `--no-half-vae` | 防止 FP16 导致的黑图/色块问题 |
| SDXL 中显存模式 | `--medvram-sdxl` | 8GB 显存专用优化，分时加载 UNet |
| 模型路径外置 | `--ckpt-dir` | 避免模型文件复制，节省磁盘空间 |

**启动配置文件** (`webui-user.bat`):
```batch
@echo off
cd /d "%~dp0"

set PYTHON=D:\ANA2\envs\sdwebui\python.exe
set VENV_DIR=-
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set HF_ENDPOINT=https://hf-mirror.com

set COMMANDLINE_ARGS=--xformers --medvram-sdxl --no-half-vae --autolaunch --theme dark --ckpt-dir "D:\迅雷下载" --controlnet-dir "models/ControlNet" --enable-insecure-extension-access

call webui.bat
```

**实测性能** (RTX 4060 8GB):
- 启动后空闲显存: ~2.7GB / 8GB
- 1024x1024 单图生成 (30 steps): ~8-12 秒
- 显存峰值: ~6.5GB

> 注: 单图 < 3 秒的目标需在更高性能 GPU (如 RTX 4090) 或开启 TensorRT/INT8 量化后达成。当前配置已尽可能优化。

### 4.3 提示词自动化：BLIP + 风格关键词

**功能描述**: 用户上传参考图后，系统自动用 BLIP 模型生成基础文字描述，再叠加选定风格关键词，降低提示词编写门槛。

**已安装组件**: BLIP 仓库 (`repositories/BLIP`)

**实现脚本**: `prompt_automation.py`

**支持风格**:
- 写实、动漫、油画、水彩、赛博朋克、像素、水墨、3D渲染

**使用方式**:
```bash
# 生成写实风格提示词
python prompt_automation.py -i input.jpg -s 写实

# 输出示例:
# 基础描述: a woman sitting on a bench in a park
# 最终正向: a woman sitting on a bench in a park, realistic, photorealistic, 8k uhd, high detail, professional photography, masterpiece, best quality, highly detailed, sharp focus
# 负向: lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit...
```

**WebUI 内置反推**: 在 img2img 界面点击 "Interrogate CLIP" / "Interrogate DeepBooru" 按钮也可自动生成提示词。

**Prompt All-in-One 提示词辅助** (扩展):
- 已安装扩展 `sd-webui-prompt-all-in-one`
- 支持中文输入自动翻译为英文提示词
- 内置提示词分类库（画质、人物、服装、场景、风格等一键添加）
- 提示词以彩色标签形式展示，支持拖动排序、调权重
- 一键插入常用负面提示词模板
- 大幅降低英文提示词编写门槛

---

## 五、部署与配置

### 5.1 目录结构

```
AI_test/test7/
├── stable-diffusion-webui/           # WebUI 主程序
│   ├── webui-user.bat                # 启动配置（已优化）
│   ├── extensions/
│   │   ├── sd-webui-controlnet/               # ControlNet 可控生成
│   │   ├── ultimate-upscale-for-automatic1111/ # 超分辨率
│   │   ├── sd-webui-prompt-all-in-one/         # 提示词辅助
│   │   └── stable-diffusion-webui-localization-zh_CN/ # 简体中文汉化
│   ├── models/
│   │   ├── Stable-diffusion/         # 主模型（外置到 D:\迅雷下载）
│   │   ├── ControlNet/               # ControlNet 模型
│   │   │   └── NoobAI-XL ControlNet_NoobAI_Controlnet_Openpose.safetensors
│   │   ├── Lora/                     # LoRA 微调模型（默认路径）
│   │   ├── VAE/                      # VAE 模型
│   │   └── ESRGAN/                   # 超分模型
│   │       └── ESRGAN_4x.pth         # 已安装
│   └── repositories/
│       └── BLIP/                     # 图像理解模型
├── prompt_automation.py              # 提示词自动化脚本
├── setup_and_verify.py               # 环境检查脚本
├── ControlNet模型下载指南.md          # 模型下载指南
└── SD-WebUI部署报告.md               # 部署过程记录
```

### 5.2 手动安装清单

由于网络环境限制，以下组件需手动下载放置：

**① ControlNet 模型** (存放于 `models/ControlNet/`):
```bash
# SDXL OpenPose 姿态控制 (轻量版, ~140MB)
curl -o models/ControlNet/control-lora-openposeXL2-rank256.safetensors \
  "https://huggingface.co/stabilityai/control-lora/resolve/main/control-lora-openposeXL2-rank256.safetensors"

# SDXL Canny 边缘控制 (轻量版, ~140MB)
curl -o models/ControlNet/control-lora-cannyXL-rank256.safetensors \
  "https://huggingface.co/stabilityai/control-lora/resolve/main/control-lora-canny-rank256.safetensors"
```

**② VAE 模型** (可选, 存放于 `models/VAE/`):
- `sdxl_vae.safetensors` 可改善色彩表现

**③ LoRA 模型** (按需, 存放于 `models/Lora/` 或 `D:\迅雷下载`):
- 从 Civitai / HuggingFace 下载社区分享的 `.safetensors` 文件

### 5.3 环境验证

运行检查脚本确认配置状态:
```bash
python setup_and_verify.py
```

---

## 六、使用指南

### 6.1 启动系统

**方式一: 命令行启动**
```bash
cd stable-diffusion-webui
D:/ANA2/envs/sdwebui/python.exe launch.py --xformers --medvram-sdxl --ckpt-dir "D:/迅雷下载"
```

**方式二: 双击启动**
直接双击 `stable-diffusion-webui/webui-user.bat`

**访问界面**: 浏览器自动打开 `http://127.0.0.1:7860`

### 6.2 启用中文界面

1. 点击顶部 **设置** 标签页
2. 左侧选择 **用户界面**
3. **Localization** 下拉框选择 **zh_CN**
4. 点击 **应用设置** → **重载界面**

### 6.3 文生图操作流程

1. 选择 **txt2img** 标签页
2. 输入正向/负向提示词（可借助 Prompt All-in-One 面板点击分类按钮快速插入）
3. 选择模型: `ERNIE-Image_Turbo版`
4. 设置分辨率 1024x1024，步数 30，CFG 7
5. 点击 **生成** 按钮

### 6.4 提示词辅助使用（Prompt All-in-One）

在文生图/图生图页面的提示词输入框旁会出现辅助面板：

| 功能 | 操作 |
|------|------|
| 中文输入 | 直接输入中文，自动翻译为英文提示词 |
| 分类插入 | 点击「画质」「人物」「服装」「场景」「风格」等按钮一键添加标签 |
| 权重调节 | 拖动标签上的滑块调整该提示词的权重 |
| 负面提示词 | 点击一键插入常用负面词模板 |

### 6.5 图生图风格转换流程

1. 选择 **img2img** 标签页
2. 上传原图
3. 输入目标风格提示词（如 `oil painting style`）
4. 设置 **Denoising strength**: 0.5 ~ 0.7
5. 点击生成

### 6.6 ControlNet 姿态控制流程

1. 展开 **ControlNet** 面板
2. 上传参考姿态图
3. **启用** 勾选，**完美像素模式** 勾选
4. **控制类型**: 选择 **OpenPose**
5. **预处理器**: `openpose_full`（自动提取骨骼）
6. **模型**: 选择 `NoobAI-XL ControlNet_NoobAI_Controlnet_Openpose`
7. **控制权重**: 1.0
8. 在提示词中描述目标人物特征，点击生成

### 6.7 超分辨率放大流程

**方式 A: Extra 标签页（快速放大）**
1. 选择 **Extras** 标签页
2. 上传低分辨率图
3. **Upscaler 1**: 选择 `ESRGAN_4x`
4. **Scale by**: 4
5. 点击生成

**方式 B: Ultimate SD Upscale（高质量）**
1. 在 img2img 中生成基础图
2. 发送到 img2img (或 Inpaint)
3. 脚本 (Script) 选择 `Ultimate SD Upscale`
4. 设置 Tile width/height: 512
5. 设置 Scale factor: 4
6. 点击生成

---

## 七、项目总结

### 7.1 已实现功能

| 功能模块 | 完成状态 | 说明 |
|----------|----------|------|
| 文生图 | 已完成 | txt2img，支持正负提示词 |
| 图生图 | 已完成 | img2img，支持重绘强度调节 |
| ControlNet 可控生成 | 已完成 | OpenPose / Canny 扩展已安装，模型需手动下载 |
| 超分辨率修复 | 已完成 | ESRGAN 已安装，Ultimate Upscale 扩展已安装 |
| 可视化界面 | 已完成 | WebUI 完整交互界面 |
| LoRA 支持 | 已完成 | 目录配置完毕，支持动态加载 |
| 推理加速 | 已完成 | xformers + FP16 + medvram-sdxl |
| 提示词自动化 | 已完成 | BLIP 脚本 + Prompt All-in-One + WebUI 内置反推 |
| 中文汉化 | 已完成 | stable-diffusion-webui-localization-zh_CN 已安装 |

### 7.2 关键技术点

1. **显存优化与参数调试**: 8GB 显存运行 SDXL 大模型，通过 `--medvram-sdxl` 分时加载 + `--xformers` 注意力优化 + FP16 半精度，实现稳定运行。过程中发现 `--precision half` 与 `--no-half-vae` 参数冲突，已修复。LoRA 路径与 checkpoint 同目录导致模型混淆，已分离至默认 `models/Lora/` 路径。

2. **可控生成与依赖修复**: ControlNet 扩展安装后加载失败，经排查为 `mediapipe 0.10.35` 新版移除 `solutions` API 导致不兼容，降级至 `0.10.8` 后修复。用户已下载 `NoobAI-XL ControlNet` 姿态模型并可用。

3. **提示词自动化**: 三层方案降低使用门槛：(1) BLIP 大模型生成基础描述；(2) `prompt_automation.py` 脚本叠加风格关键词库；(3) 安装 `Prompt All-in-One` 扩展，支持中文输入自动翻译、分类标签一键插入、可视化权重调节，配合 WebUI 内置 Interrogate 反推，形成完整提示词辅助体系。

4. **超分辨率**: 结合 ESRGAN 快速放大与 Ultimate SD Upscale AI 重绘，兼顾速度和质量。

### 7.3 后续优化方向

| 方向 | 方案 |
|------|------|
| INT8 量化 | 使用 `sd-webui-tensorrt` 扩展将 UNet 转为 TensorRT INT8 引擎，进一步加速 2-3 倍 |
| 批量生成 | 结合 Prompt S/R 脚本实现批量风格对比 |
| API 服务 | 基于 WebUI 的 `--api` 模式封装 RESTful 接口，支持外部系统调用 |
| 云端部署 | 使用 --share 参数生成 Gradio 公网链接，或部署至阿里云/AutoDL |

---

**报告日期**: 2026-05-11
**作者**: [课程作业]
