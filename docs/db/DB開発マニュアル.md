# DB開発マニュアル

このプロジェクトでは、SQLAlchemyのモデル定義とAlembicのマイグレーション履歴を使ってDBスキーマを管理します。

## ディレクトリ構成

```text
backend/
├── app/db/models.py                     # SQLAlchemyモデル
├── alembic.ini                          # Alembic設定
├── alembic/
│   ├── env.py                           # DB接続とモデル読込
│   └── versions/                        # マイグレーション履歴
└── scripts/migrate.sh                   # 本番・開発用の適用スクリプト
```

## DB接続設定

`DATABASE_URL` に接続先を指定します。

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"
```

未指定の場合は、`backend/alembic.ini` に設定されたローカル開発用の接続先が使用されます。

本番環境では、パスワードをリポジトリに保存せず、コンテナ環境変数やシークレット管理機能から渡してください。

## 初回マイグレーション

空のDBにスキーマを作成する場合は、以下を実行します。

```bash
cd backend
source .venv/bin/activate

export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"
./scripts/migrate.sh
```

`migrate.sh` は内部で以下を実行します。

```bash
python -m alembic upgrade head
```

Alembicは `alembic_version` テーブルで適用済みのリビジョンを管理します。そのため、同じコマンドを複数回実行しても、適用済みのマイグレーションは再実行されません。

## モデル変更の手順

### 1. モデルを変更する

SQLAlchemyモデルを `backend/app/db/models.py` に追加・変更します。

### 2. マイグレーションを自動生成する

```bash
cd backend
python -m alembic revision --autogenerate -m "変更内容"
```

`backend/alembic/versions/` にファイルが作成されます。

自動生成された内容は必ず確認してください。特に以下を確認します。

- `upgrade()` が期待するDDLになっているか
- `downgrade()` で安全に戻せるか
- カラムのNULL許可、型、デフォルト値が正しいか
- 外部キー、インデックス、制約が正しいか
- 既存データがある場合に、NULL不可カラムを追加していないか

### 3. 開発DBへ適用する

```bash
./scripts/migrate.sh
```

### 4. 状態を確認する

```bash
python -m alembic current
python -m alembic heads
python -m alembic history
```

## 本番環境への適用

本番デプロイでは、アプリケーション起動前にマイグレーションを適用します。

```bash
cd backend
DATABASE_URL="${PRODUCTION_DATABASE_URL}" ./scripts/migrate.sh
```

推奨する適用順序は以下です。

1. DBのバックアップを取得する
2. 新しいアプリケーションイメージを準備する
3. `./scripts/migrate.sh` を実行する
4. `python -m alembic current` で適用状況を確認する
5. アプリケーションを起動・切り替えする

アプリケーションの起動処理ではスキーマ変更を行いません。スキーマはAlembicでのみ変更します。

## 既存DBをAlembic管理下へ移行する場合

既存DBに `create_all()` で作成されたテーブルがある場合、いきなり `upgrade head` を実行すると、既存テーブルと初回マイグレーションが重複して失敗する可能性があります。

まず、既存DBのスキーマが `0001_initial_schema` と一致していることを確認してください。確認後、初回だけ以下を実行します。

```bash
cd backend
python -m alembic stamp 0001_initial_schema
```

`stamp` はDDLを実行せず、Alembicの適用済み状態だけを記録します。スキーマが一致していない状態で実行しないでください。

以降は通常どおりマイグレーションを作成・適用します。

```bash
python -m alembic revision --autogenerate -m "次の変更"
./scripts/migrate.sh
```

## ロールバック

直前のリビジョンへ戻す場合:

```bash
python -m alembic downgrade -1
```

特定のリビジョンへ戻す場合:

```bash
python -m alembic downgrade <revision_id>
```

本番でのロールバックは、データの削除や非可逆な変更を伴う可能性があります。実行前にDBバックアップを取得し、対象リビジョンの `downgrade()` を確認してください。

## マイグレーション作成時の注意

- 生成されたマイグレーションファイルを必ずコミットする
- 既存のマイグレーションファイルを書き換えない
- 本番適用済みのリビジョンを削除・変更しない
- データ移行が必要な場合は、DDLとデータ更新の順序を明示する
- 大量データの更新は長時間ロックやタイムアウトに注意する
- 複数ブランチで同時にリビジョンを作成した場合は、マージリビジョンを検討する

## よく使うコマンド

```bash
# 現在のDBのリビジョン
python -m alembic current

# 最新リビジョン
python -m alembic heads

# 履歴
python -m alembic history

# 未適用分をすべて適用
./scripts/migrate.sh

# 1つ戻す
python -m alembic downgrade -1

# SQLだけ生成（DBは変更しない）
python -m alembic upgrade head --sql
```
