#!/usr/bin/env bash
# verify_env.sh — 컨테이너 안에서 주요 패키지 상태를 한눈에 확인
set -e

echo "=============================="
echo " 환경 검증 스크립트"
echo "=============================="

echo ""
echo "[1] Python"
python -V

echo ""
echo "[2] PyTorch / CUDA"
python -c "
import torch
print(f'  torch        : {torch.__version__}')
print(f'  CUDA avail   : {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  CUDA version : {torch.version.cuda}')
    print(f'  GPU          : {torch.cuda.get_device_name(0)}')
else:
    print('  (GPU 미인식 — CPU 모드로 진행 가능)')
"

echo ""
echo "[3] 주요 패키지 버전"
python -c "
pkgs = [
    'torchvision','transformers','datasets','diffusers','accelerate',
    'peft','trl','bitsandbytes','unsloth',
    'langchain','langgraph','chromadb',
    'numpy','matplotlib','pandas','scipy','scikit-learn',
    'PIL','tqdm','tiktoken',
]
for p in pkgs:
    try:
        mod = __import__(p)
        ver = getattr(mod, '__version__', 'OK')
        print(f'  {p:20s} {ver}')
    except ImportError:
        print(f'  {p:20s} ❌ NOT FOUND')
    except Exception as e:
        print(f'  {p:20s} ❌ ERROR: {e}')
"

echo ""
echo "[4] JupyterLab"
jupyter lab --version 2>/dev/null || echo "  ❌ jupyterlab not found"

echo ""
echo "=============================="
echo " 검증 완료"
echo "=============================="
