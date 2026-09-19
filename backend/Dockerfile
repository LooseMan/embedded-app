# ==============================================================================
# 1. BASE STAGE
# ==============================================================================
# ADR: Pythonの公式イメージはDebian系であるため、Red Hat系をベースにしたいという
# 要件に基づきAlmaLinuxを選択。OS更新（dnf update）はイメージ肥大化とビルド遅延、
# 破壊を防ぐため実施せず、公式イメージの定期更新に依存する。
FROM almalinux:10 AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /workspace

# ADR: AlmaLinux 10に内蔵されているOS標準のPython 3.12環境をそのまま利用し、
# パッケージマネージャー（dnf）による追加インストールを排除してビルドを高速化する。
COPY requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

# ==============================================================================
# 2. DEVELOPMENT STAGE
#    - コマンド: docker build --target dev -t fastapi-dev .
# ==============================================================================
FROM base AS dev

RUN uv pip install --no-cache pytest httpx pytest-asyncio

# ADR: コードはイメージに同梱せず、ホストからマウントして利用する。
# これにより、コード変更時のイメージ再ビルドを回避し、開発効率を向上させる。

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# 3. PRODUCTION STAGE
#    - コマンド: docker build -t fastapi-prod .
# ==============================================================================
FROM base AS prod

COPY app ./app

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
