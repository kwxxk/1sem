# ============================================================
# SSAFY AI 역량 평가 Docker 이미지
# Base : PyTorch 2.7 + CUDA 12.8 (RTX 50xx / Blackwell 대응)
# Python : 3.10
# ============================================================
FROM python:3.11-slim

# ── 1. 환경 변수 ────────────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Seoul \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ── 2. 시스템 패키지 (최소한) ────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl wget tzdata libgl1 libglib2.0-0 gcc g++ && \
    ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ── 3. 작업 디렉터리 ────────────────────────────────────────
WORKDIR /workspace

# ── 4. Python 패키지 설치 ───────────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── 5. 검증 스크립트 복사 ───────────────────────────────────
COPY scripts/verify_env.sh /usr/local/bin/verify_env.sh
RUN chmod +x /usr/local/bin/verify_env.sh

# ── 6. 포트 & 실행 ─────────────────────────────────────────
EXPOSE 8888
CMD ["bash", "-lc", "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=${JUPYTER_TOKEN:-lab} --ServerApp.allow_origin='*'"]
