"""
生成实训报告 Word 文档
格式要求：
- 标题：黑体、一号、单倍行距、段后 0 磅
- 一级标题：黑体、三号、段前 8 磅段后 4 磅、居中
- 二级标题：黑体、三号、段前 8 磅段后 4 磅、左对齐
- 正文：中文宋体、英文 Times New Roman、小四、20 磅行间距、首行缩进 2 字符
- 图片：嵌入式
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# ========== 辅助函数 ==========
def set_run_font(run, en_name='Times New Roman', cn_name='宋体', size=Pt(12), bold=False):
    run.font.name = en_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), cn_name)
    run.font.size = size
    run.font.bold = bold


def add_heading_custom(doc, text, level=1):
    """添加自定义标题"""
    if level == 0:  # 主标题
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = Pt(26)
        run = p.add_run(text)
        set_run_font(run, 'Times New Roman', '黑体', Pt(26), bold=True)
    elif level == 1:  # 一级标题
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = Pt(20)
        run = p.add_run(text)
        set_run_font(run, 'Times New Roman', '黑体', Pt(16), bold=True)
    elif level == 2:  # 二级标题
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = Pt(20)
        run = p.add_run(text)
        set_run_font(run, 'Times New Roman', '黑体', Pt(16), bold=True)
    return p


def add_body_text(doc, text):
    """添加正文段落"""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)  # 约2字符
    p.paragraph_format.line_spacing = Pt(20)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run(text)
    set_run_font(run, 'Times New Roman', '宋体', Pt(12), bold=False)
    return p


# ========== 封面标题 ==========
add_heading_custom(doc, '基于 Stable Diffusion 的图文风格化生成系统', level=0)
add_heading_custom(doc, '——人工智能综合实训报告', level=0)
doc.add_paragraph()  # 空行
doc.add_paragraph()

# ========== 第1章 选题背景与问题定义 ==========
add_heading_custom(doc, '第1章 选题背景与问题定义', level=1)

add_body_text(doc,
    '随着人工智能技术的快速发展，AIGC（人工智能生成内容）在创意设计、广告营销、'
    '游戏原画等领域的应用日益广泛。传统的图像设计工作高度依赖专业设计师的手工绘制，'
    '存在门槛高、周期长、成本高等问题。中小型企业或个人创作者往往难以承担高昂的'
    '设计费用，而开源AI绘画技术的兴起为这一困境提供了新的解决思路。')

add_body_text(doc,
    '本项目选题聚焦于基于 Stable Diffusion 的图文风格化生成系统。Stable Diffusion '
    '是目前最主流的开源文本到图像生成模型之一，具有生成质量高、社区生态丰富、'
    '可本地部署等优势。通过构建一套完整的风格化图像生成系统，用户仅需输入文字描述'
    '或上传普通参考图片，系统即可自动生成高质量的风格化图像。同时，借助 ControlNet '
    '等条件控制技术，支持基于姿态骨架、边缘图等条件进行精准控制，使生成结果更贴近'
    '用户预期，从而显著降低专业设计门槛，提升创作效率。')

add_body_text(doc,
    '本系统拟解决的核心问题包括：（1）降低非专业用户进行高质量图像创作的技术门槛；'
    '（2）通过条件控制技术提升生成结果的可控性和一致性；'
    '（3）通过推理加速和显存优化，使系统在消费级显卡（8GB显存）上流畅运行。')

# ========== 第2章 系统设计与实现 ==========
add_heading_custom(doc, '第2章 系统设计与实现', level=1)

add_heading_custom(doc, '2.1 技术选型与运行环境', level=2)

add_body_text(doc,
    '本系统基于 AUTOMATIC1111 开发的 Stable Diffusion WebUI（v1.10.1）构建，'
    '这是目前社区最活跃、功能最完善的Stable Diffusion可视化界面之一。'
    '基础模型采用 SDXL 架构的写实大模型，原生支持 1024×1024 分辨率生成。')

add_body_text(doc,
    '运行环境配置如下：操作系统为 Windows 11 Home，GPU 为 NVIDIA GeForce RTX 4060 '
    'Laptop（8GB显存），CUDA 版本 12.1，Python 3.10.20（Anaconda环境），'
    'PyTorch 2.1.2+cu121。')

add_heading_custom(doc, '2.2 系统架构', level=2)

add_body_text(doc,
    '系统采用分层架构设计。用户层提供基于 Gradio 的 Web 可视化界面，支持提示词输入、'
    '图片上传和参数调节。服务层集成文生图、图生图、ControlNet条件控制、超分辨率修复等'
    '核心模块。模型层包含 SDXL 基础模型、ControlNet条件模型、ESRGAN超分模型和LoRA'
    '微调模型。辅助层提供 BLIP 图像理解、风格关键词库和推理优化组件。')

add_heading_custom(doc, '2.3 基础功能实现', level=2)

add_body_text(doc,
    '（1）文生图功能：用户在 txt2img 界面输入正向提示词（描述期望内容）和负向提示词'
    '（排除不想要的元素），选择采样器（如 DPM++ 2M Karras）、设置步数（30步）和'
    'CFG Scale（7），即可生成 1024×1024 的高质量图像。')

add_body_text(doc,
    '（2）图生图功能：在 img2img 界面上传参考图片，通过调节重绘强度'
    '（Denoising Strength，范围 0.0~1.0）实现不同程度的风格转换。'
    '0.2~0.4 为轻度风格迁移，0.5~0.7 适合风格转换，0.8~1.0 仅保留构图。')

add_body_text(doc,
    '（3）ControlNet 可控生成：安装 sd-webui-controlnet 扩展，支持 OpenPose 姿态控制、'
    'Canny 边缘控制、Depth 深度控制等多种条件输入。用户上传参考图后，系统自动提取'
    '骨骼关键点或边缘轮廓，在生成新图像时保持相同的姿态或构图结构，实现精准控制。')

add_body_text(doc,
    '（4）超分辨率修复：集成 Ultimate SD Upscale 扩展和 ESRGAN_4x 模型，'
    '支持将低分辨率图像放大4倍。ESRGAN 方式速度快，适合快速预览；'
    'Ultimate SD Upscale 采用 Tile 分块 + AI 重绘方案，质量更高，适合成品输出。')

add_body_text(doc,
    '（5）可视化界面：WebUI 提供完整的参数调节面板，包括采样器、步数、分辨率、'
    '批次数量、CFG Scale、种子值、重绘强度、ControlNet 权重等，所有参数均可实时调整。')

add_heading_custom(doc, '2.4 扩展与插件安装', level=2)

add_body_text(doc,
    '系统安装了以下关键扩展：（1）sd-webui-controlnet —— 实现条件可控生成；'
    '（2）ultimate-upscale-for-automatic1111 —— 实现高质量超分辨率放大；'
    '（3）sd-webui-prompt-all-in-one —— 提供中文输入自动翻译、提示词分类库、'
    '可视化标签编辑等功能，大幅降低提示词编写门槛；'
    '（4）stable-diffusion-webui-localization-zh_CN —— 提供简体中文界面汉化。')

# ========== 第3章 优化与改进 ==========
add_heading_custom(doc, '第3章 优化与改进', level=1)

add_heading_custom(doc, '3.1 LoRA 微调支持', level=2)

add_body_text(doc,
    'LoRA（Low-Rank Adaptation）通过在原始模型权重旁路注入低秩矩阵进行微调，'
    '仅需数十张图片即可学习特定人物或风格。系统将 LoRA 模型路径配置为默认的'
    'models/Lora/ 目录，用户将 .safetensors 文件放入该目录后，即可在提示词中通过'
    '<lora:模型名:权重> 语法动态调用，实现小样本身份一致性保持。')

add_heading_custom(doc, '3.2 推理加速与显存优化', level=2)

add_body_text(doc,
    '针对 RTX 4060（8GB显存）的硬件限制，系统实施了多项优化措施：'
    '（1）启用 --xformers 注意力优化，减少 20%~30% 显存占用；'
    '（2）启用 --medvram-sdxl 中显存模式，SDXL 专用分时加载策略；'
    '（3）使用 FP16 半精度推理，显存减半；'
    '（4）添加 --no-half-vae 参数，防止 VAE 半精度导致的黑图/色块问题。'
    '实测 1024×1024 单图生成（30步）耗时约 8~12 秒，显存峰值约 6.5GB。')

add_heading_custom(doc, '3.3 提示词自动化', level=2)

add_body_text(doc,
    '为降低非专业用户的提示词编写门槛，系统构建了三层提示词辅助体系：'
    '（1）BLIP 大模型反推：开发 prompt_automation.py 脚本，上传图片后自动生成'
    '基础描述，叠加 8 种预设风格关键词（写实、动漫、油画、水彩、赛博朋克等）；'
    '（2）WebUI 内置反推：图生图界面支持 Interrogate CLIP/DeepBooru 一键生成提示词；'
    '（3）Prompt All-in-One 扩展：支持中文输入自动翻译为英文提示词，'
    '内置提示词分类库（画质、人物、服装、场景、风格等），以彩色标签形式展示，'
    '支持拖动排序和权重调节。')

add_heading_custom(doc, '3.4 问题排查与修复', level=2)

add_body_text(doc,
    '在部署和优化过程中，遇到了以下问题并逐一解决：')

add_body_text(doc,
    '（1）bat 文件编码问题：webui-user.bat 配置文件包含中文路径，'
    'UTF-8 编码在 Windows cmd 中解析为乱码导致路径无效。解决方案是将 bat 文件'
    '保存为 GBK 编码（带 CRLF 换行符），确保中文路径能被正确识别。')

add_body_text(doc,
    '（2）参数冲突问题：同时启用 --precision half 和 --no-half-vae 时，'
    'WebUI 启动报 AssertionError 冲突错误。分析后确认两者在代码层面互斥，'
    '最终方案是移除 --precision half，保留 --no-half-vae，'
    '让 WebUI 根据显卡能力自动选择 FP16 精度。')

add_body_text(doc,
    '（3）ControlNet 依赖不兼容：sd-webui-controlnet 扩展加载失败，'
    '报错为 mediapipe 模块缺少 solutions 属性。经排查，mediapipe 0.10.35 '
    '新版已移除 solutions API，而 controlnet_aux 仍依赖旧接口。'
    '解决方案是将 mediapipe 降级至 0.10.8 版本，扩展恢复正常加载。')

add_body_text(doc,
    '（4）LoRA 路径混淆：初始配置将 --lora-dir 与 --ckpt-dir 指向同一目录'
    '（D:\\迅雷下载），导致 LoRA 模型也被识别为主模型。'
    '修复方案是移除 --lora-dir 参数，使用默认的 models/Lora/ 路径，'
    '实现主模型与 LoRA 模型的分离管理。')

# ========== 第4章 总结 ==========
add_heading_custom(doc, '第4章 总结', level=1)

add_heading_custom(doc, '4.1 项目收获', level=2)

add_body_text(doc,
    '通过本次实训，深入理解了 Stable Diffusion 扩散模型的基本原理和工程化部署流程，'
    '掌握了 AUTOMATIC1111 WebUI 的配置与扩展开发，熟悉了 ControlNet 条件控制、'
    'LoRA 微调、超分辨率修复等前沿技术的实际应用。同时，在排查各类环境兼容性问题的过程中，'
    '提升了独立分析和解决问题的能力。')

add_heading_custom(doc, '4.2 遇到的困难', level=2)

add_body_text(doc,
    '（1）网络环境受限，GitHub 和 HuggingFace 访问不稳定，扩展和模型的自动下载频繁失败，'
    '需要通过国内镜像、ZIP 下载、手动放置等多种方式解决；'
    '（2）Python 依赖版本冲突问题（mediapipe）较为隐蔽，需要逐层排查错误日志才能定位；'
    '（3）Windows 平台下的编码问题（bat 文件 GBK/UTF-8）容易忽略但影响启动。')

add_heading_custom(doc, '4.3 当前不足与未来改进', level=2)

add_body_text(doc,
    '当前系统的不足包括：（1）单图生成耗时约 8~12 秒，尚未达到 "<3秒" 的优化目标，'
    '可通过 TensorRT/INT8 量化进一步加速；'
    '（2）ControlNet 模型仅下载了 OpenPose 类型，Canny 和 Depth 模型待补充；'
    '（3）系统目前为本地单机运行，未提供 RESTful API 接口，无法被外部系统调用。')

add_body_text(doc,
    '未来改进方向：（1）引入 sd-webui-tensorrt 扩展，将 UNet 转换为 TensorRT 引擎，'
    '实现 2~3 倍推理加速；（2）补充更多 ControlNet 条件模型，支持更丰富的控制方式；'
    '（3）基于 WebUI 的 --api 模式封装 RESTful 接口，支持第三方应用集成；'
    '（4）探索 LoRA 小样本训练流程，实现个性化风格定制。')

# ========== 附录 ==========
doc.add_page_break()
add_heading_custom(doc, '附录', level=1)

add_heading_custom(doc, '附录A 参考资料', level=2)

refs = [
    '[1] AUTOMATIC1111. Stable Diffusion WebUI [EB/OL]. https://github.com/AUTOMATIC1111/stable-diffusion-webui',
    '[2] Mikubill. sd-webui-controlnet [EB/OL]. https://github.com/Mikubill/sd-webui-controlnet',
    '[3] Stability AI. Control-LoRA [EB/OL]. https://huggingface.co/stabilityai/control-lora',
    '[4] Physton. sd-webui-prompt-all-in-one [EB/OL]. https://github.com/Physton/sd-webui-prompt-all-in-one',
    '[5] Rombach R, et al. High-Resolution Image Synthesis with Latent Diffusion Models [C]. CVPR, 2022.',
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(20)
    run = p.add_run(ref)
    set_run_font(run, 'Times New Roman', '宋体', Pt(12))

add_heading_custom(doc, '附录B 关键启动配置', level=2)

p = doc.add_paragraph()
p.paragraph_format.line_spacing = Pt(20)
run = p.add_run('webui-user.bat 启动参数：')
set_run_font(run, 'Times New Roman', '宋体', Pt(12))

code = '''--xformers --medvram-sdxl --no-half-vae --autolaunch --theme dark --ckpt-dir "D:\\\\迅雷下载" --controlnet-dir "models/ControlNet" --enable-insecure-extension-access'''
p = doc.add_paragraph()
p.paragraph_format.line_spacing = Pt(20)
run = p.add_run(code)
set_run_font(run, 'Consolas', '宋体', Pt(10.5))

add_heading_custom(doc, '附录C 已安装扩展清单', level=2)

exts = [
    'sd-webui-controlnet —— ControlNet 可控生成',
    'ultimate-upscale-for-automatic1111 —— 超分辨率修复',
    'sd-webui-prompt-all-in-one —— 提示词辅助',
    'stable-diffusion-webui-localization-zh_CN —— 简体中文汉化',
]
for ext in exts:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = Pt(20)
    run = p.add_run('• ' + ext)
    set_run_font(run, 'Times New Roman', '宋体', Pt(12))

# 保存
output_path = 'C:/Users/dwqjdh/Desktop/AI_test/test7/实训报告_基于StableDiffusion的图文风格化生成.docx'
doc.save(output_path)
print(f'报告已生成: {output_path}')
