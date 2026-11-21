#!/usr/bin/env bash
set -euo pipefail

# macOSのDocker Desktop上で、backend/compose.yamlを操作する開発用ラッパー。
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly COMPOSE_FILE="${COMPOSE_FILE:-${SCRIPT_DIR}/compose.yaml}"
readonly COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-embedded-app}"
readonly DB_READY_TIMEOUT="${DB_READY_TIMEOUT:-60}"

usage() {
    echo "Usage: $0 [start|stop]"
}

compose() {
    docker compose \
        --file "${COMPOSE_FILE}" \
        --project-name "${COMPOSE_PROJECT_NAME}" \
        "$@"
}

wait_for_database() {
    local attempt

    echo "Waiting for the database to be ready (timeout: ${DB_READY_TIMEOUT}s)..."
    for ((attempt = 1; attempt <= DB_READY_TIMEOUT; attempt++)); do
        if compose exec -T db pg_isready -U user -d dbname >/dev/null 2>&1; then
            echo "Database is ready!"
            return 0
        fi
        sleep 1
    done

    echo "PostgreSQL did not become ready within ${DB_READY_TIMEOUT}s." >&2
    echo "Recent PostgreSQL logs:" >&2
    compose logs --tail 50 db >&2 || true
    return 1
}

open_api_docs() {
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:8000/docs"
    else
        echo "Please open http://localhost:8000/docs in your web browser."
    fi
}

main() {
    local action="${1:-start}"

    case "${action}" in
        start|up)
            echo "Starting API and PostgreSQL with Docker Compose..."
            compose up --detach --build
            wait_for_database
            open_api_docs
            ;;
        stop|down)
            echo "Stopping application services..."
            # stopはコンテナだけを停止し、名前付きボリュームは保持する。
            compose stop
            echo "Application services stopped. Docker volumes were kept."
            ;;
        -h|--help)
            usage
            ;;
        *)
            usage >&2
            return 2
            ;;
    esac
}

main "$@"
