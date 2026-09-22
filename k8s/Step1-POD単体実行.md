# Kubernetes 開発構成

`backend/launch_container.sh` のDocker構成を、FastAPIとPostgreSQLを同一Podで起動する手順です。対象はローカル開発・検証環境です。

本番環境では、Pod単体ではなくDeployment、Service、外部のSecret管理、バックアップ可能なデータベース構成を使用してください。

## 構成

- FastAPI: `backend/Dockerfile` の `prod` ステージ
- PostgreSQL: 17
- DB接続: Pod内の `localhost:5432`
- FastAPI公開: `hostPort: 8000`
- DBデータ: PersistentVolumeClaim（PVC）
- Kubernetesマニフェスト: [`prod.yml`](./prod.yml)
- Podman手順: [`PODMAN.md`](./PODMAN.md)

## 前提

- Docker DesktopのKubernetesが有効
- `kubectl` と `docker` がPATHに存在
- リポジトリルートでコマンドを実行
- Docker DesktopのKubernetesコンテキストが `docker-desktop`

クラスタとコンテキストを確認します。

```sh
kubectl config use-context docker-desktop
kubectl get nodes
```

次のようにノードが `Ready` なら起動できます。

```text
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   ...
```

Docker DesktopのKubernetesの有効化方法は、[Docker Desktop公式ドキュメント](https://docs.docker.com/desktop/use-desktop/kubernetes/)を参照してください。

## 起動

### 1. FastAPIイメージを作成する

Kubernetesでは、アプリケーションコードを含む `prod` ステージを使用します。`dev` ステージはソースコードのバインドマウントを前提とするため、このPodには使用しません。

```sh
docker build --target prod -t my-fastapi:prod backend
docker image inspect my-fastapi:prod >/dev/null
```

`docker image inspect` が終了コード0なら、ローカルイメージが作成されています。

Docker Desktopの `docker-desktop` クラスタでは、DockerのローカルイメージストアをPodから参照できます。マニフェストには `imagePullPolicy: IfNotPresent` を指定しているため、同名イメージがローカルにあればレジストリから取得しません。

### 2. DB用Secretを作成する

Secretはリポジトリへ保存しません。次の値は開発用の例です。共有環境では、強度のあるパスワードと適切なSecret管理を使用してください。

```sh
DB_PASSWORD='change-me'
kubectl create secret generic embedded-app-db \
  --from-literal=password="$DB_PASSWORD" \
  --from-literal=database-url="postgresql+asyncpg://user:${DB_PASSWORD}@localhost:5432/dbname" \
  --dry-run=client -o yaml | kubectl apply -f -
```

次のように `created` または `configured` と表示されれば、Secretが作成または更新されています。

```text
secret/embedded-app-db created
```

### 3. Podを作成する

```sh
kubectl apply -f k8s/prod.yml
kubectl wait --for=condition=Ready pod/embedded-app --timeout=120s
```

`kubectl wait` が終了コード0で完了し、次の確認結果が `2/2 Running` になれば、PostgreSQLとFastAPIの両方がReadyです。

```sh
kubectl get pod embedded-app
```

```text
NAME           READY   STATUS    RESTARTS   AGE
embedded-app   2/2     Running   0          ...
```

### 4. 疎通を確認する

`hostPort` を使わず、ローカルへ一時的にポート転送する場合は、別ターミナルで次を実行します。

```sh
kubectl port-forward pod/embedded-app 8000:8000
```

次の表示が出ている間、ポート転送が有効です。

```text
Forwarding from 127.0.0.1:8000 -> 8000
```

さらに別のターミナルで確認します。

```sh
curl -i http://localhost:8000/readyz
```

HTTPステータスが `200 OK` なら、FastAPIが起動し、DB接続を含むReady判定に成功しています。

### 5. DB migrationを適用する

migrationはPod起動時には自動実行されません。

```sh
cd backend
./scripts/migrate.sh
```

Alembicの各migrationが適用されたことを確認してから、アプリケーションを利用してください。

## 再作成・停止

イメージやマニフェストを変更した場合は、Podを再作成します。PVCは削除しないため、DBデータは保持されます。

```sh
kubectl delete pod embedded-app
kubectl apply -f k8s/prod.yml
kubectl wait --for=condition=Ready pod/embedded-app --timeout=120s
```

Podの削除が完了し、再作成されたPodが `2/2 Running` になれば完了です。

停止時もPodだけを削除します。

```sh
kubectl delete pod embedded-app
```

PVCを削除するとDBデータも削除される可能性があります。データを明示的に削除する場合だけ実行してください。

```sh
kubectl delete pvc postgres-data
```

削除後に次を実行し、PVCが表示されなければ削除されています。

```sh
kubectl get pvc postgres-data
```

## トラブルシューティング

### ImagePullBackOff

ローカルイメージの名前・タグと、`prod.yml` の `spec.containers[].image` が一致しているか確認します。

```sh
docker image ls my-fastapi
kubectl describe pod embedded-app
```

Docker Desktopのイメージストアでは、次の画像のようにイメージ名とタグを確認できます。

![Docker Desktopのイメージストア](./DockerDesktop-ImageStore.png)

`docker-desktop` 以外のクラスタでは、クラスタのノードへイメージを転送する必要があります。

### Probe失敗・再起動

コンテナログとイベントを確認します。

```sh
kubectl logs embedded-app -c my-fastapi --tail=100
kubectl describe pod embedded-app
```

次を確認します。

- FastAPIが `0.0.0.0:8000` で起動している
- `/healthz` がHTTP `200` を返す
- `/readyz` がHTTP `200` を返す
- `DATABASE_URL` の接続先がPod内の `localhost:5432` になっている

### PodがPendingのままになる

PVCの状態とイベントを確認します。

```sh
kubectl get pvc postgres-data
kubectl describe pod embedded-app
```

PVCが `Bound`、Podが `Running` になれば、ストレージの準備は完了しています。

## Probeとデータ保持

- PostgreSQLの `readinessProbe`: `pg_isready` でDBの受付状態を確認します。
- FastAPIの `readinessProbe`: `/readyz` でアプリケーションとDB接続を確認します。
- FastAPIの `livenessProbe`: `/healthz` が失敗した場合にコンテナを再起動します。
- `postgres-data`: PVCで管理するため、Podだけを削除してもDBデータは保持されます。
- `emptyDir`: Pod削除時に内容が消えるため、PostgreSQLの永続化には使用しません。

## 将来のクラウド移行

この構成はローカルKubernetesでの検証を目的としています。クラウドや本番環境では、通常は次のように発展させます。

- Pod → Deployment
- `hostPort` → Service / Ingress
- PVC → クラウドのStorageClass
- Secret → Secret Managerなど
- Pod内PostgreSQL → マネージドDBまたは別StatefulSet
