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

`FileCategory`、`File`、`FileSet`は、一覧・詳細取得・作成・更新・削除を提供します。
`FileSetRel`は複合主キー（`file_set_id`、`file_id`）の関連テーブルのため、一覧・詳細取得・作成・削除を提供します。

| リソース | エンドポイント |
| --- | --- |
| FileCategory | `/file-categories` |
| File | `/files` |
| FileSet | `/file-sets` |
| FileSetRel | `/file-set-relations` |
