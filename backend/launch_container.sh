#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
    echo "Usage: $0 [start|stop]"
}

ACTION="${1:-start}"
case "$ACTION" in
    start|up)
        ;;
    stop)
        echo "Stopping application containers..."
        docker stop my-fastapi my-postgres >/dev/null 2>&1 || true
        echo "Application containers stopped. Docker volumes were kept."
        exit 0
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

# Wait for the docker to be ready
echo "Waiting for Docker to be ready..."
until docker info > /dev/null 2>&1; do
	sleep 1
done

# Create container network
CONTAINER_NETWORK="web-back-network"
docker network inspect "$CONTAINER_NETWORK" >/dev/null 2>&1 || \
    docker network create "$CONTAINER_NETWORK" >/dev/null

# Start psql container
DB_CONTAINER="my-postgres"
# postgresを無指定で使うとメジャーアップデートでデータディレクトリ仕様が変わるため固定する。
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:17}"
# DBはホストOSのパスを直接指定せず、Docker管理の名前付きボリュームに保存する。
# これにより、macOS・Linux・Windowsで保存先の差異をDocker側に隠蔽できる。
DB_VOLUME="embedded-app-postgres-data"
docker volume create "$DB_VOLUME" >/dev/null

if docker ps -aq -f "name=^${DB_CONTAINER}$" | grep -q .; then
    DB_MOUNT="$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Type}}:{{.Name}}{{end}}{{end}}' "${DB_CONTAINER}")"
    if [[ "$DB_MOUNT" != "volume:${DB_VOLUME}" ]]; then
        echo "Warning: ${DB_CONTAINER} does not use the named volume ${DB_VOLUME}." >&2
        echo "The existing container will be reused to preserve its data." >&2
    fi
fi

if docker ps -q -f "name=^${DB_CONTAINER}$" | grep -q .; then
    echo "PostgreSQL container is already running."

elif docker ps -aq -f "name=^${DB_CONTAINER}$" | grep -q .; then
    echo "Starting existing PostgreSQL container..."
    docker start "${DB_CONTAINER}"

else
    echo "Creating PostgreSQL container..."
    docker run --name "${DB_CONTAINER}" \
        -p 5432:5432 \
        --network "$CONTAINER_NETWORK" \
        --mount "type=volume,source=${DB_VOLUME},target=/var/lib/postgresql/data" \
        -e POSTGRES_USER=user \
        -e POSTGRES_PASSWORD=password \
        -e POSTGRES_DB=dbname \
        -d "${POSTGRES_IMAGE}"
fi

# Wait for the database to be ready
DB_READY_TIMEOUT="${DB_READY_TIMEOUT:-60}"
echo "Waiting for the database to be ready (timeout: ${DB_READY_TIMEOUT}s)..."
db_ready=false
for ((attempt = 1; attempt <= DB_READY_TIMEOUT; attempt++)); do
    if docker exec "${DB_CONTAINER}" pg_isready -U user -d dbname >/dev/null 2>&1; then
        db_ready=true
        break
    fi
    sleep 1
done

if [[ "$db_ready" != true ]]; then
    echo "PostgreSQL did not become ready within ${DB_READY_TIMEOUT}s." >&2
    echo "Recent PostgreSQL logs:" >&2
    docker logs --tail 50 "${DB_CONTAINER}" >&2 || true
    exit 1
fi
echo "Database is ready!"

# Open the FastAPI server in the default web browser
if command -v xdg-open > /dev/null; then
	# for Linux
	xdg-open http://localhost:8000/docs
elif command -v open > /dev/null; then
	# for macOS
	open http://localhost:8000/docs
else
	echo "Please open http://localhost:8000 in your web browser."
fi

# Start api container
API_CONTAINER="my-fastapi"

if docker ps -q -f "name=^${API_CONTAINER}$" | grep -q .; then
    echo "FastAPI container is already running."

elif docker ps -aq -f "name=^${API_CONTAINER}$" | grep -q .; then
    echo "Starting existing FastAPI container..."
    docker start "${API_CONTAINER}"

else
    echo "Creating FastAPI container..."
    # ソースコードは開発中の編集内容を即時反映するため、ホストからバインドマウントする。
    docker run --name "${API_CONTAINER}" \
        -p 8000:8000 \
        --network "$CONTAINER_NETWORK" \
        -e DATABASE_URL="postgresql+asyncpg://user:password@${DB_CONTAINER}:5432/dbname" \
        --mount "type=bind,source=${SCRIPT_DIR},target=/workspace" \
        -d fastapi-dev
fi

# Run tests in the FastAPI container
# $ docker exec -it my-fastapi pytest
