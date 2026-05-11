"""
系统配置检查与验证脚本
验证 Stable Diffusion WebUI 环境及扩展安装状态
"""
import os
import sys
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBUI_DIR = os.path.join(BASE_DIR, "stable-diffusion-webui")
MODELS_DIR = os.path.join(WEBUI_DIR, "models")
EXT_DIR = os.path.join(WEBUI_DIR, "extensions")


def check_dir(path, label):
    exists = os.path.exists(path)
    status = "存在" if exists else "缺失"
    print(f"  [{status}] {label}: {path}")
    return exists


def check_file(path, label):
    exists = os.path.exists(path)
    size = os.path.getsize(path) // (1024 * 1024) if exists else 0
    status = f"存在 ({size}MB)" if exists else "缺失"
    print(f"  [{status}] {label}")
    return exists


def check_python_env():
    print("\n【Python 环境检查】")
    py_path = os.environ.get("PYTHON", r"D:\ANA2\envs\sdwebui\python.exe")
    if os.path.exists(py_path):
        result = subprocess.run([py_path, "--version"], capture_output=True, text=True)
        print(f"  [存在] Python: {result.stdout.strip()}")
    else:
        print(f"  [缺失] Python: {py_path}")

    try:
        import torch
        print(f"  [存在] PyTorch: {torch.__version__}")
        print(f"  [存在] CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  [存在] CUDA 版本: {torch.version.cuda}")
            print(f"  [存在] GPU: {torch.cuda.get_device_name(0)}")
            print(f"  [存在] 显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    except ImportError:
        print("  [缺失] PyTorch 未安装")


def check_extensions():
    print("\n【扩展安装检查】")
    extensions = [
        ("sd-webui-controlnet", "ControlNet 可控生成"),
        ("ultimate-upscale-for-automatic1111", "Ultimate SD Upscale 超分辨率"),
    ]
    all_ok = True
    for ext_name, desc in extensions:
        path = os.path.join(EXT_DIR, ext_name)
        ok = check_dir(path, desc)
        all_ok = all_ok and ok
    return all_ok


def check_models():
    print("\n【模型文件检查】")
    checks = []

    # 主模型（通过 --ckpt-dir 指定外部目录）
    ckpt_dir = r"D:\迅雷下载"
    has_ckpt = False
    if os.path.exists(ckpt_dir):
        files = [f for f in os.listdir(ckpt_dir) if f.endswith((".safetensors", ".ckpt"))]
        if files:
            print(f"  [存在] 主模型目录: {ckpt_dir} ({len(files)} 个模型)")
            has_ckpt = True
        else:
            print(f"  [警告] 主模型目录为空: {ckpt_dir}")
    else:
        print(f"  [缺失] 主模型目录: {ckpt_dir}")
    checks.append(has_ckpt)

    # VAE
    vae_dir = os.path.join(MODELS_DIR, "VAE")
    vae_files = [f for f in os.listdir(vae_dir) if f.endswith((".safetensors", ".pt", ".ckpt"))] if os.path.exists(vae_dir) else []
    if vae_files:
        print(f"  [存在] VAE 模型: {len(vae_files)} 个")
    else:
        print(f"  [警告] VAE 模型缺失（可选，但推荐）")

    # LoRA
    lora_dir = os.path.join(MODELS_DIR, "Lora")
    lora_files = [f for f in os.listdir(lora_dir) if f.endswith((".safetensors", ".pt"))] if os.path.exists(lora_dir) else []
    if lora_files:
        print(f"  [存在] LoRA 模型: {len(lora_files)} 个")
    else:
        print(f"  [警告] LoRA 模型缺失（如需小样本微调需下载）")

    # ControlNet
    cn_dir = os.path.join(MODELS_DIR, "ControlNet")
    cn_files = [f for f in os.listdir(cn_dir) if f.endswith((".safetensors", ".pth"))] if os.path.exists(cn_dir) else []
    if cn_files:
        print(f"  [存在] ControlNet 模型: {len(cn_files)} 个")
    else:
        print(f"  [缺失] ControlNet 模型（需手动下载，见文档）")
    checks.append(len(cn_files) > 0)

    # ESRGAN 超分
    esrgan_dir = os.path.join(MODELS_DIR, "ESRGAN")
    esrgan_files = [f for f in os.listdir(esrgan_dir) if f.endswith((".pth", ".safetensors"))] if os.path.exists(esrgan_dir) else []
    if esrgan_files:
        print(f"  [存在] ESRGAN 超分模型: {len(esrgan_files)} 个")
    else:
        print(f"  [缺失] ESRGAN 超分模型")
    checks.append(len(esrgan_files) > 0)

    return checks


def check_webui_config():
    print("\n【WebUI 启动配置检查】")
    bat_path = os.path.join(WEBUI_DIR, "webui-user.bat")
    if not os.path.exists(bat_path):
        print("  [缺失] webui-user.bat")
        return

    with open(bat_path, "r", encoding="utf-8") as f:
        content = f.read()

    params = [
        ("--xformers", "xformers 注意力优化"),
        ("--medvram-sdxl", "8GB 显存 SDXL 优化"),
        ("--precision half", "半精度推理"),
        ("--no-half-vae", "VAE 全精度（防止黑图）"),
        ("--lora-dir", "LoRA 模型路径"),
        ("--controlnet-dir", "ControlNet 模型路径"),
    ]

    for flag, desc in params:
        status = "已启用" if flag in content else "未启用"
        print(f"  [{status}] {desc} ({flag})")


def print_summary(results):
    print("\n" + "=" * 50)
    print("【检查总结】")
    if all(results):
        print("所有核心组件已就绪，可以启动 WebUI！")
    else:
        print("部分组件缺失，请参考文档完成配置。")
    print("=" * 50)


def main():
    print("=" * 50)
    print("Stable Diffusion WebUI 环境检查工具")
    print("=" * 50)

    check_dir(WEBUI_DIR, "WebUI 根目录")
    check_python_env()
    ext_ok = check_extensions()
    model_checks = check_models()
    check_webui_config()

    print_summary([ext_ok] + model_checks)


if __name__ == "__main__":
    main()
