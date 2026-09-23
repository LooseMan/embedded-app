# Kubernetes Deployment 構成

`k8s/prod.yml` の単体 Pod 構成を、FastAPI と PostgreSQL を分離した構成へ発展させます。FastAPI は Deployment で 2 レプリカ、PostgreSQL は StatefulSet で 1 レプリカとして管理します。

## 構成

```text
外部クライアント
        |
        v
backend-api-svc:30080 (NodePort)
        |
        +--> backend-api-xxxxx-1 (FastAPI)
        |
        +--> backend-api-xxxxx-2 (FastAPI)
                              |
                              v
                    postgres-db:5432
                              |
                              v
                     postgres-db-0
                              |
                              v
                     専用 PVC 1Gi
```

| リソース | 設定 | 役割 |
| --- | --- | --- |
| `backend-api` Deployment | 2 レプリカ | FastAPI を水平スケールする |
| `backend-api-svc` Service | NodePort `30080` → Pod `8000` | FastAPI への入口と負荷分散 |
| `postgres-db` StatefulSet | 1 レプリカ | PostgreSQL と Pod の識別子を管理する |
| `postgres-db` Service | ヘッドレス、TCP `5432` | FastAPI から DB Pod へ接続する |
| `postgres-storage` PVC | `ReadWriteOnce`、1Gi | PostgreSQL のデータを保持する |

マニフェストは [`deployment.yml`](./deployment.yml) です。FastAPI に `hostPort` は設定せず、Service 経由で公開します。

## 前提

- Docker Desktop の Kubernetes が有効
- `kubectl` と `docker` が PATH に存在する
- リポジトリルートでコマンドを実行する
- Kubernetes コンテキストが `docker-desktop` である
- `my-fastapi:prod` イメージをクラスタから参照できる

## 起動

### 1. FastAPI イメージを作成する

```sh
docker build --target prod -t my-fastapi:prod backend
docker image inspect my-fastapi:prod >/dev/null
```

### 2. DB 用 Secret を作成する

Secret はリポジトリへ保存しません。次の値は開発用の例です。

```sh
DB_PASSWORD='change-me'
kubectl create secret generic db-credentials \
  --from-literal=password="$DB_PASSWORD" \
  --from-literal=database-url="postgresql+asyncpg://user:${DB_PASSWORD}@postgres-db:5432/dbname" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. リソースを作成する

```sh
kubectl apply -f k8s/deployment.yml
kubectl rollout status statefulset/postgres-db --timeout=120s
kubectl rollout status deployment/backend-api --timeout=120s
kubectl get pods
```

DB が `1/1 Running`、FastAPI が 2 Pod とも `1/1 Running` になり、両方の rollout が終了コード 0 なら起動完了です。

### 4. API に接続する

NodePort の標準範囲は通常 `30000`〜`32767` です。この構成では `30080` を固定しているため、Docker Desktop では次で接続できます。

```sh
curl -i http://localhost:30080/readyz
```

HTTP ステータスが `200 OK` なら、NodePort と Service を経由して FastAPI に接続できています。NodePort を利用できない環境では、次を代替手段にします。

```sh
kubectl port-forward service/backend-api-svc 8000:8000
curl -i http://localhost:8000/readyz
```

### 5. DB migration を適用する

DB Service をローカルへ転送します。

```sh
kubectl port-forward service/postgres-db 5432:5432
```

別ターミナルで migration を 1 回だけ実行します。

```sh
cd backend
DATABASE_URL="postgresql+asyncpg://user:change-me@localhost:5432/dbname" ./scripts/migrate.sh
```

## リクエストと起動シーケンス

### リクエストの流れ

NodePort `30080` に届いたリクエストは、`backend-api-svc` の selector に一致する Ready な FastAPI Pod のいずれか 1 つへ転送されます。Pod の IP や名前をクライアントが直接指定することはありません。

- 2 つの FastAPI Pod は同じ `postgres-db` Service に接続し、同じ PostgreSQL のデータを読み書きする。
- API Pod のローカルメモリやファイルにセッション・業務データを保存しない。必要な状態は DB、Redis、署名付きトークンなどで共有する。
- Pod 障害時は、readinessProbe に失敗した Pod が転送先から外れる。処理途中のリクエストは失敗する可能性があるため、再試行と API の冪等性を設計する。

### 起動の流れ

`kubectl apply` は DB の Ready 完了まで API Deployment の作成を保証しません。API Pod の `initContainer` と `readinessProbe` で、利用可能になる条件を制御します。

1. `postgres-db-0` を起動する。
2. API Pod の `wait-for-database` が `postgres-db:5432` の受付開始まで待つ。
3. DB 接続可能になったら FastAPI コンテナを起動する。
4. `/readyz` が成功した API Pod を Service の転送先に追加する。

DB 障害などで initContainer が待機中の場合、API Pod は `Init` 状態になります。これは API が DB なしでリクエストを受けないための動作であり、DB のレプリケーションやフェイルオーバーを実現するものではありません。

## 更新・停止

イメージまたはマニフェストを変更した場合は、再適用して両方の rollout を確認します。

```sh
kubectl apply -f k8s/deployment.yml
kubectl rollout status statefulset/postgres-db --timeout=120s
kubectl rollout status deployment/backend-api --timeout=120s
```

停止時は Deployment、API Service、StatefulSet、DB Service を削除します。StatefulSet の PVC は残るため、DB データも保持されます。

```sh
kubectl delete deployment/backend-api service/backend-api-svc statefulset/postgres-db service/postgres-db
```

DB データを明示的に削除する場合だけ、生成された PVC を削除します。

```sh
kubectl delete pvc postgres-storage-postgres-db-0
```

## トラブルシューティング

### PostgreSQL が Pending、FastAPI が Init:0/1 のままになる

次のような状態の場合、FastAPI ではなく PostgreSQL の PVC が未接続です。

```text
postgres-db-0                  0/1   Pending
backend-api-xxxxx              0/1   Init:0/1
```

PVC の状態とイベントを確認します。

```sh
kubectl get pvc
kubectl describe pvc postgres-storage-postgres-db-0
```

次のイベントが表示される場合、StorageClass は存在するものの、PVC を作成するプロビジョナが動作していません。

```text
Waiting for a volume to be created by the external provisioner 'docker.io/hostpath'
```

Docker Desktop の Kubernetes を再起動します。

1. Docker Desktop の Settings で Kubernetes を開く。
2. Kubernetes を一度 Disable して Apply する。
3. Kubernetes を再度 Enable して Apply する。

プロビジョナが復旧すると、PVC は自動的に `Bound` になります。

```sh
kubectl get pvc -w
kubectl get pods
```

次の状態になれば復旧しています。

```text
postgres-storage-postgres-db-0   Bound
postgres-db-0                     1/1   Running
backend-api-xxxxx                1/1   Running
```

`backend-api` の `Init:0/1` は、`wait-for-database` が PostgreSQL の起動を待っている状態です。PostgreSQL が Ready になれば、FastAPI の initContainer が完了して API コンテナが起動します。

Kubernetes の Reset やクラスタ再作成は、既存リソースや DB データを削除する可能性があります。StorageClass とプロビジョナの状態を確認する前に実行しないでください。

## Deployment 化で追加検討する項目

- **可用性**: レプリカ数、Pod のノード偏り、`PodDisruptionBudget` の要否を決める。
- **更新**: `RollingUpdate`、`maxUnavailable`、`maxSurge`、ロールバック方法を決める。
- **リソース**: CPU・メモリの `requests` と `limits`、ノード容量、スケジューリング制約を設定する。
- **状態管理**: Pod のローカル領域に依存せず、データの所有者、バックアップ、復旧方法を決める。
- **設定管理**: ConfigMap、Secret、Secret Manager、設定変更時の再起動方法を決める。
- **監視**: readiness・liveness・startup probe、ログ、メトリクス、障害通知を設計する。
- **終了処理**: graceful shutdown、`terminationGracePeriodSeconds`、`preStop` を設計する。

## DB の運用上の注意

この構成は FastAPI と PostgreSQL を分離したローカル検証用です。PostgreSQL は 1 レプリカであり、StatefulSet の `replicas` を 2 へ変更してもレプリケーション、フェイルオーバー、バックアップは自動的に実現しません。

本番では、PostgreSQL の冗長化方式、書き込み先の切り替え、バックアップ・リストア、migration の実行主体とタイミングを別途設計します。運用負荷を下げるには、マネージド PostgreSQL の利用も検討します。
