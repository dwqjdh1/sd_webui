# 基于 Stable Diffusion 的图文风格化生成系统

人工智能综合实训项目 - 基于 AUTOMATIC1111 WebUI 的图文风格化生成系统。

## 项目概述

面向创意设计、广告营销、游戏原画等场景，用户输入文字或上传普通图片，系统自动生成高质量风格化图像，支持 ControlNet 条件控制、超分辨率修复等功能。

## 文件结构

```
├── webui-user.bat              # WebUI启动配置文件
├── prompt_automation.py        # BLIP提示词自动化脚本
└── setup_and_verify.py         # 环境检查脚本
```

## 部署步骤

### 1. 克隆 Stable Diffusion WebUI

```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
```

### 2. 安装扩展

将本仓库的 `webui-user.bat` 复制到 WebUI 目录，启动时会自动安装以下扩展：

- `sd-webui-controlnet` - ControlNet可控生成
- `ultimate-upscale-for-automatic1111` - 超分辨率修复
- `sd-webui-prompt-all-in-one` - 提示词辅助
- `stable-diffusion-webui-localization-zh_CN` - 中文汉化

或手动安装：

```bash
cd stable-diffusion-webui/extensions
git clone https://github.com/Mikubill/sd-webui-controlnet.git
git clone https://github.com/Coyote-A/ultimate-upscale-for-automatic1111.git
git clone https://github.com/Physton/sd-webui-prompt-all-in-one.git
git clone https://github.com/dtlnor/stable-diffusion-webui-localization-zh_CN.git
```

### 3. 下载模型

- **主模型**: 放入 `models/Stable-diffusion/` 或通过 `--ckpt-dir` 指定外部目录
- **ControlNet模型**: 放入 `models/ControlNet/`（从 Civitai 或 HuggingFace 下载 SDXL 版本）
- **ESRGAN超分模型**: 自动下载或手动放入 `models/ESRGAN/`

### 4. 启动 WebUI

双击 `webui-user.bat` 或命令行启动：

```bash
cd stable-diffusion-webui
python launch.py --xformers --medvram-sdxl --no-half-vae --ckpt-dir "模型路径"
```

## 环境要求

- Python 3.10.x
- PyTorch 2.x + CUDA 12.x
- NVIDIA GPU (推荐 8GB+ 显存)
- Windows 10/11

## 功能列表

| 功能 | 说明 |
|------|------|
| 文生图 | txt2img，支持正向/负向提示词 |
| 图生图 | img2img，支持重绘强度调节 |
| ControlNet | 姿态/边缘等条件控制 |
| 超分辨率 | 4倍放大 + AI细节修复 |
| 提示词辅助 | 中文输入自动翻译、分类标签 |
| 中文界面 | 简体中文汉化 |

## 参考资料

- [AUTOMATIC1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [ControlNet 扩展](https://github.com/Mikubill/sd-webui-controlnet)
- [Prompt All-in-One](https://github.com/Physton/sd-webui-prompt-all-in-one)

## 作者

人工智能综合实训项目 - 2026年5月