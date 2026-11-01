# Backend

## セットアップ

```sh
pip-compile
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 構成

責務ごとに HTTP、業務処理、DB 永続化を分離しています。

```text
app/
├── api/                    # FastAPI の router と API 入出力
│   ├── routes.py           # routerの集約
│   ├── dependencies.py     # 共通依存性
│   ├── health.py
│   ├── files.py
│   └── schemas/            # 機能別の入出力スキーマ
│       └── files.py
├── services/               # ユースケース・業務処理
│   └── files.py
├── db/                     # DB 接続、ORM モデル、Repository
│   ├── base.py
│   ├── session.py
│   ├── models.py
│   └── repositories/
│       └── files.py
├── main.py                 # FastAPI の組み立て
└── stream_logger.py        # ロギング基盤
```

依存方向は `api → services → db.repositories` とし、ORM モデルや SQLAlchemy の
セッションを HTTP ルートに直接書かない方針です。DB スキーマの変更は引き続き
Alembic で管理します。

PostgreSQLは`postgres:17`に固定しています。無指定の`postgres`を使うとメジャーアップデートでデータディレクトリ仕様が変わるためです。`embedded-app-postgres-data`はDockerの名前付きボリュームで、コンテナを削除してもPostgreSQLのデータは残ります。別のイメージを使う場合は、`POSTGRES_IMAGE=postgres:16 ./launch_container.sh start`のように指定します。

DBデータにはホストOSのパスを直接指定せず、Docker管理の名前付きボリュームを使っています。OSごとの保存先の違いをDocker側に隠蔽し、コンテナを再作成してもデータを保持するためです。一方、アプリケーションのソースコードは開発中の変更を即時反映する必要があるため、ホストからコンテナへバインドマウントしています。

```sh
docker volume rm embedded-app-postgres-data
```

コンテナの起動は次で行います。既に起動中なら再利用し、停止中なら起動するため、繰り返し実行できます。既存のPostgreSQLコンテナが名前付きボリュームを使っていない場合も、データを保護するためそのコンテナを再利用して警告を表示します。PostgreSQLの起動待ちには60秒のタイムアウトがあります。待機時間は`DB_READY_TIMEOUT=120 ./launch_container.sh start`のように変更できます。

```sh
./launch_container.sh start
```

APIとPostgreSQLをまとめて停止する場合は、次を実行します。停止ではボリュームを削除しません。

```sh
./launch_container.sh stop
```

| クラス                  | 継承元         | 用途                 |
| -------------------- | ----------- | ------------------ |
| **Pydantic Model**   | `BaseModel` | APIの入力・出力（JSON）    |
| **SQLAlchemy Model** | `Base`      | データベースのテーブル定義（ORM） |

## File API

`FileCategory`、`File`、`FileSet`は、一覧・詳細取得・作成・更新・削除を提供します。`FileSetRel`はDB内部の関連テーブルとして保持し、APIではFileSet配下のファイル操作として扱います。

| リソース | エンドポイント |
| --- | --- |
| FileCategory | `/file-categories` |
| File | `/files` |
| FileSet | `/file-sets` |
| FileSetのファイル一覧 | `/file-sets/{file_set_id}/files` |
| FileSetへのファイル追加 | `PUT /file-sets/{file_set_id}/files/{file_id}` |
| FileSetからのファイル削除 | `DELETE /file-sets/{file_set_id}/files/{file_id}` |

## APIテスト

リポジトリのルートで次を実行すると、`backend/tests` のAPIテストを詳細表示で実行できます。

```sh
pytest
```

`backend/tests/conftest.py` の設定により、実行したテスト名と各テストの結果が表示されます。
APIテストはフェーズ別に次のフォルダへ配置します。

- `backend/tests/unit`: 提出前にローカルで実行し、DB・外部マイクロサービスを使わずAPIルートとServiceを単体検証します。
- `backend/tests/integ`: Push時のGitLab CIで起動済みバックエンドへHTTP接続し、テスト専用PostgreSQLコンテナを使ってRepositoryを含む業務フローの期待値を比較します。本番DB・外部マイクロサービスの接続先は使用しません。
- `backend/tests/e2e`: 将来、フロントエンドを含むE2Eテストを配置する予定です。

提出前の単体テストはリポジトリルートで次を実行します。

```sh
pytest backend/tests/unit
```

単体テストではRepositoryをモックし、APIの委譲とServiceの引数変換・業務ルールを検証します。結合テストはPush時に `.gitlab-ci.yml` から実行され、CIではバックエンドを起動してHTTP経由で接続し、テスト用PostgreSQLへAlembicを適用してから、`tests/integ`だけを実行します。
ローカルで実行する場合は、先にバックエンドとテスト用DBを起動し、必要に応じて`BACKEND_BASE_URL`で接続先を指定します。

```sh
./launch_container.sh start
BACKEND_BASE_URL=http://localhost:8000 pytest tests/integ
```

File APIの結合テストでは、リソースの作成・取得・更新・関連付け・解除・削除を
まとめて確認します。結合テストにはPostgreSQLが必要です。
