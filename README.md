# embedded-app

## 構成

- `backend/`: FastAPI、SQLAlchemy、Alembic によるバックエンド
- `frontend/`: TypeScript + Next.js で実装予定のフロントエンド
- `docs/`: 設計資料と開発マニュアル

## Backend

責務ごとにAPI、サービス、Repository、ORMモデルを分離しています。

```text
backend/app/
├── api/                  # FastAPIのrouterと入出力スキーマ
│   ├── routes.py         # routerの集約
│   ├── health.py
│   ├── files.py          # File系CRUD API
│   └── schemas/files.py
├── services/             # ユースケース
├── db/models.py          # SQLAlchemyモデル
└── db/repositories/      # DB永続化処理
```

### 開発コンテナ

```sh
cd backend
./launch_container.sh start
```

既に起動中のコンテナは再利用し、停止中のコンテナは起動します。既存DBが名前付きボリューム未使用でも、データ保護のため再利用して警告を表示します。PostgreSQLの起動待ちには60秒のタイムアウトがあり、起動できない場合はコンテナログを表示して終了します。待機時間は`DB_READY_TIMEOUT=120 ./launch_container.sh start`のように変更できます。停止する場合は次を実行します。

```sh
./launch_container.sh stop
```

PostgreSQLは`postgres:17`に固定し、データはDockerの名前付きボリューム`embedded-app-postgres-data`に保存します。無指定の`postgres`を使うとメジャーアップデートでデータディレクトリ仕様が変わるためです。ホストOS固有のパスを使わないため、macOS・Linux・Windowsで同じ設定を利用でき、コンテナを再作成してもデータを保持できます。ボリュームを削除するとデータも失われます。別のイメージを使う場合は、`POSTGRES_IMAGE=postgres:16 ./launch_container.sh start`のように指定します。

スキーマを初期化・更新する場合は、DB起動後にAlembicを実行します。

```sh
cd backend
./scripts/migrate.sh
```

### File API

`FileCategory`、`File`、`FileSet`は一覧・詳細取得・作成・更新・削除、`FileSetRel`は複合主キーのため一覧・詳細取得・作成・削除を提供します。

| リソース | エンドポイント |
| --- | --- |
| FileCategory | `/file-categories` |
| File | `/files` |
| FileSet | `/file-sets` |
| FileSetRel | `/file-set-relations` |

## VS Code設定

### プロジェクト設定

推奨拡張は `.vscode/extensions.json` で管理します。拡張のバージョンは固定しません。

プロジェクト共通設定は `.vscode/settings.json` で管理し、文字コードの自動推測を有効にしています。

### アプリケーション設定

VS Code本体と拡張の更新を手動管理する場合は、コマンドパレットから `Preferences: Open Application Settings (JSON)`を開き、次を追加します。

自動更新はVS Code全体に影響するアプリケーション設定のため、プロジェクトの `.vscode/settings.json` では共有できません。

```json
{
  "update.mode": "none",
  "extensions.autoUpdate": "off"
}
```

特定の拡張だけ停止する場合は、拡張ビューの歯車メニューから`Auto Update`を無効にします。

macOSとWindowsではこの設定でVS Code本体の自動更新を停止できます。Linuxでは、インストールに使用したディストリビューションのパッケージマネージャー側で更新を管理します。
