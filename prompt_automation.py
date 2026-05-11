"""
提示词自动化脚本
基于 BLIP 自动生成图像基础描述，叠加风格关键词
降低用户学习成本，提升创作效率
"""
import sys
import os
import argparse
import torch
from PIL import Image

# 添加 BLIP 到路径
BLIP_PATH = os.path.join(os.path.dirname(__file__), "stable-diffusion-webui", "repositories", "BLIP")
sys.path.insert(0, BLIP_PATH)

from models.blip import blip_decoder

# 风格关键词库
STYLE_KEYWORDS = {
    "写实": "realistic, photorealistic, 8k uhd, high detail, professional photography",
    "动漫": "anime style, manga, cel shading, vibrant colors, studio ghibli",
    "油画": "oil painting, impressionist, rich colors, canvas texture, fine art",
    "水彩": "watercolor painting, soft edges, pastel colors, artistic, flowing",
    "赛博朋克": "cyberpunk, neon lights, futuristic, dystopian, high tech low life",
    "像素": "pixel art, retro game style, 16-bit, dithering, nostalgic",
    "水墨": "chinese ink wash painting, monochrome, brush strokes, poetic, traditional",
    "3D渲染": "3d render, octane render, blender, cinematic lighting, ray tracing",
}

QUALITY_BOOST = "masterpiece, best quality, highly detailed, sharp focus"
NEGATIVE_PROMPT = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"


def load_blip_model(device="cuda" if torch.cuda.is_available() else "cpu"):
    """加载 BLIP 图像描述模型"""
    model_url = "https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_large_caption.pth"
    model_path = os.path.join(os.path.dirname(__file__), "models", "blip_model_large_caption.pth")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        print(f"正在下载 BLIP 模型到 {model_path} ...")
        import urllib.request
        urllib.request.urlretrieve(model_url, model_path)
        print("下载完成")

    model = blip_decoder(pretrained=model_path, image_size=384, vit="large")
    model.eval()
    model = model.to(device)
    return model, device


def generate_caption(image_path, model, device, max_length=50):
    """为图片生成基础描述"""
    image = Image.open(image_path).convert("RGB")
    from torchvision import transforms
    from torchvision.transforms.functional import InterpolationMode

    transform = transforms.Compose([
        transforms.Resize((384, 384), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        caption = model.generate(image, sample=False, num_beams=3, max_length=max_length, min_length=5)
    return caption[0]


def build_prompt(base_caption, style="写实", add_quality=True):
    """叠加风格关键词，构建最终提示词"""
    style_kw = STYLE_KEYWORDS.get(style, STYLE_KEYWORDS["写实"])
    prompt = f"{base_caption}, {style_kw}"
    if add_quality:
        prompt += f", {QUALITY_BOOST}"
    return prompt


def main():
    parser = argparse.ArgumentParser(description="SD 提示词自动化工具")
    parser.add_argument("--image", "-i", required=True, help="输入图片路径")
    parser.add_argument("--style", "-s", default="写实", choices=list(STYLE_KEYWORDS.keys()), help="目标风格")
    parser.add_argument("--no-quality", action="store_true", help="不添加质量增强词")
    parser.add_argument("--output", "-o", help="输出文件路径（默认打印到控制台）")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"错误: 图片不存在 {args.image}")
        sys.exit(1)

    print("正在加载 BLIP 模型...")
    model, device = load_blip_model()
    print(f"使用设备: {device}")

    print(f"正在分析图片: {args.image}")
    caption = generate_caption(args.image, model, device)
    print(f"\n基础描述: {caption}")

    final_prompt = build_prompt(caption, args.style, not args.no_quality)
    print(f"\n风格: {args.style}")
    print(f"最终正向提示词:\n{final_prompt}")
    print(f"\n推荐负向提示词:\n{NEGATIVE_PROMPT}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"正向提示词: {final_prompt}\n")
            f.write(f"负向提示词: {NEGATIVE_PROMPT}\n")
        print(f"\n已保存到: {args.output}")


if __name__ == "__main__":
    main()
