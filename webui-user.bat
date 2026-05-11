@echo off
cd /d "%~dp0"

set PYTHON=D:\ANA2\envs\sdwebui\python.exe
set GIT=
set VENV_DIR=-
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set HF_ENDPOINT=https://hf-mirror.com

set STABLE_DIFFUSION_REPO=https://github.com/joypaul162/Stability-AI-stablediffusion.git
set STABLE_DIFFUSION_COMMIT_HASH=f16630a927e00098b524d687640719e4eb469b76
set STABLE_DIFFUSION_XL_COMMIT_HASH=
set K_DIFFUSION_COMMIT_HASH=
set BLIP_COMMIT_HASH=
set ASSETS_COMMIT_HASH=

set COMMANDLINE_ARGS=--xformers --medvram-sdxl --no-half-vae --autolaunch --theme dark --ckpt-dir "D:\Ñ¸À×ÏÂÔØ" --controlnet-dir "models/ControlNet" --enable-insecure-extension-access

call webui.bat
