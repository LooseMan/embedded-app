#!/usr/bin/env bash
set -euo pipefail

# Configuration
readonly DB_CONTAINER="my-postgres"
readonly POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:17}"
readonly DB_VOLUME="postgres-data"
readonly DB_USER="user"
readonly DB_PASSWORD="password"
readonly DB_NAME="dvdrental"
readonly DB_PORT="5432"
readonly DB_DATA_DIR="/var/lib/postgresql/data"

# コンテナ・ボリュームの削除
# docker stop|start|rm -f my-postgres
# docker volume rm postgres-data

# # ログ表示
# docker logs my-postgres

# # 最新ログを追跡
# docker logs -f --tail 100 my-postgres

# # 稼働中コンテナ一覧
# docker ps

# # 停止中も含めた状態
# docker ps -a --filter name=^my-postgres$

# # 詳細なステータス
# docker inspect --format '{{.State.Status}}' my-postgres

container_status() {
    local container_name="$1"

    docker inspect --format '{{.State.Status}}' "$container_name" 2>/dev/null || true
}

ensure_postgres_container() {
    local container_name="$1"
    local postgres_image="$2"
    local db_volume="$3"
    local status

    docker volume create "$db_volume" >/dev/null
    status="$(container_status "$container_name")"

    case "$status" in
        running)
            ;;
        created|paused|restarting|removing|exited|dead)
            docker start "$container_name" >/dev/null
            ;;
        "")
            docker run --name "$container_name" \
                -p "${DB_PORT}:${DB_PORT}" \
                --mount "type=volume,source=${db_volume},target=${DB_DATA_DIR}" \
                -e "POSTGRES_USER=${DB_USER}" \
                -e "POSTGRES_PASSWORD=${DB_PASSWORD}" \
                -e "POSTGRES_DB=${DB_NAME}" \
                -d "$postgres_image" >/dev/null
            ;;
        *)
            echo "Unsupported container state: $status" >&2
            return 1
            ;;
    esac
}

wait_for_database() {
    local container_name="$1"
    local db_user="$2"
    local db_name="$3"

    until docker exec "$container_name" pg_isready -U "$db_user" -d "$db_name" >/dev/null 2>&1; do
        sleep 1
    done
}

main() {
    ensure_postgres_container "$DB_CONTAINER" "$POSTGRES_IMAGE" "$DB_VOLUME"
    wait_for_database "$DB_CONTAINER" "$DB_USER" "$DB_NAME"
    docker exec -it "$DB_CONTAINER" "$@"
}

main "$@"
