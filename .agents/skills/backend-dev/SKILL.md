---
name: backend-dev
description: embedded-appのFastAPI、SQLAlchemy、Alembic、PostgreSQLを使ったバックエンドDB開発ルール。
---

# Backend DB development

このSkillは、`backend/`のDBスキーマ、ORMモデル、Repository、migration、DB接続を変更するときに適用する。

## Architecture

依存方向は次の順序にする。

```text
API router / schema → service → repository → SQLAlchemy model / session
```

- `backend/app/db/models.py`: SQLAlchemy ORMモデル
- `backend/app/db/repositories/`: SQLAlchemyを使った永続化処理
- `backend/app/services/`: ユースケースとトランザクション単位の業務処理
- `backend/app/api/`: HTTPルートとPydantic入出力スキーマ
- `backend/alembic/versions/`: 適用可能なmigration履歴

HTTPルートにSQLAlchemyのクエリやセッション操作を直接書かない。APIで扱う関係は、DBの中間テーブルをそのまま公開せず、所有側のリソース配下で操作する。たとえば`FileSetRel`はDB内部の関連テーブルとして保持し、APIでは`/file-sets/{file_set_id}/files`で扱う。

## Model and migration rules

- DBスキーマの正はAlembicのmigration履歴とし、アプリケーション起動時に`create_all()`を実行しない。
- ORMモデルを変更したら、対応するmigrationを作成・レビュー・コミットする。
- 適用済みのmigrationファイルは書き換えない。修正は新しいmigrationで行う。
- `--autogenerate`の出力を必ず確認し、NULL制約、デフォルト値、外部キー、インデックス、制約、既存データへの影響を手動で検証する。
- NULL不可カラムの追加や型変更など、既存データに影響する変更は、データ移行とDDLの順序を明示する。
- 外部キーと複合主キーを使う関連テーブルでは、削除時の整合性とAPIからの公開範囲を明確にする。

## Migration workflow

DB接続先は`DATABASE_URL`で指定する。パスワードをソースコードやコミット済みファイルに書かない。

```sh
cd backend
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"

# 変更後にmigrationを作成
python -m alembic revision --autogenerate -m "describe the schema change"

# 未適用migrationを適用
./scripts/migrate.sh

# 状態を確認
python -m alembic current
python -m alembic heads
python -m alembic history
```

`./scripts/migrate.sh`は未適用分だけを適用するため、繰り返し実行できる。migration適用前に、必要に応じてDBバックアップを取得する。本番でのdowngradeはデータ損失や非可逆変更の有無を確認してから行う。

既存DBをAlembic管理下へ移行する場合は、スキーマが対象migrationと一致することを確認してから`alembic stamp`を使う。未確認の状態でstampしない。

## Repository and transaction rules

- RepositoryはSQLAlchemyの永続化処理に集中させ、HTTP固有の例外やレスポンス形式を持ち込まない。
- Serviceは複数Repositoryにまたがる処理、存在確認、業務ルールを担当する。
- 作成・更新・削除はトランザクション境界を明確にし、例外時はrollback可能な状態を維持する。
- 外部キー違反、重複キー、存在しないリソースは、未処理のDB例外として500にせず、API層で適切な4xxへ変換する。
- セットアップ、migration、関連付け操作は、同じ操作を繰り返しても安全な冪等性を基本とする。

## Docker and persistence

- 開発DBは`backend/launch_container.sh start`で起動し、`stop`で停止する。
- PostgreSQLイメージのタグは固定し、`latest`相当の無指定タグを使わない。
- DBデータはDockerの名前付きボリュームに保存し、ホストOS固有のDBパスを指定しない。
- コンテナの再作成時にボリュームを削除しない。データ削除は明示的な別操作とする。
- ソースコードの即時反映が必要な場合だけ、ホストからコンテナへバインドマウントする。
- PostgreSQLのメジャーバージョンを変更する場合は、先に`pg_dump`などでバックアップし、互換性とデータ移行手順を確認する。

## Validation checklist

DB変更後は、可能な範囲で次を実行する。

1. `python -m compileall -q backend/app`
2. `python -m alembic upgrade head`
3. `python -m alembic current`で想定リビジョンを確認
4. DB接続を伴うRepository／APIテスト
5. OpenAPIに公開するエンドポイントと、DBの外部キー・制約の整合性を確認

検証できない環境依存事項、未適用のmigration、バックアップ未実施事項は最終報告に明記する。
