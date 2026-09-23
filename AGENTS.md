# Agent instructions

このファイルは、`embedded-app` リポジトリで作業するエージェント向けの指示です。
ユーザーの依頼と競合する場合は、ユーザーの依頼を優先してください。

## Repository map

- `backend/`: FastAPI、SQLAlchemy、Alembic
- `frontend/`: TypeScript、Next.js
- `docs/`: 設計資料、開発マニュアル
- `tests/`: テストとテスト手順
- `backend/app/api/`: ヘルスチェックとFile系API
- `backend/app/db/repositories/`: DB永続化処理

## Change rules

- 作業前に対象ファイルと関連実装を確認する。
- 既存の未コミット変更を上書き・破棄しない。
- 依頼範囲外の変更を追加しない。
- 既存ファイルをリファクタリングなどで書き換える場合は、既存コメントに設計判断が含まれる可能性があるため、内容を最大限尊重する。ただし、誤記は修正し、より簡潔でわかりやすい表現には積極的に置き換える。
- ターミナルのコピペを含む実動作ログは信頼性の高い検証情報であるため、割愛・編集せず、内容を最大限尊重する。
- セットアップや運用スクリプトは、同じ操作を繰り返しても安全な冪等性を基本とする。
- 既存リソースを再利用し、データを削除・破棄する処理は明示的な操作として分離する。
- 設定、依存関係、運用方法を変更したら、関連ドキュメントも更新する。
- 秘密情報、環境固有のパス、生成物をコミット対象にしない。

## Documentation and UML

- ドキュメントは簡潔に書き、事実と手順を中心に記述する。
- UMLはPlantUMLで記述し、Markdownには次の形式で埋め込む。

  ```plantuml
  @startuml
  <UML本文>
  @enduml
  ```

- Markdown全体のプレビューにはMarkdown Preview Enhanced（MPE）を使う。
- 図単位のプレビューにはPlantUML（PUML）拡張を使う。
- 図を追加・変更した場合は、目的と前提を文書から分かるようにする。

## Project conventions

- Kubernetesなど複数のリソースを定義する設定では、識別子を役割単位で命名する。アプリケーション全体の名前をDeployment、Service、PVC、Secret、ラベルのすべてに機械的に繰り返さず、`backend-api`、`backend-api-svc`、`postgres-storage`、`db-credentials`のように対象の役割が分かる名前を使う。selectorとその対象ラベルなど、意味的な対応付けに必要な重複は許容する。
- Python依存関係は `backend/requirements.in` を編集元、`backend/requirements.txt` を固定結果として扱う。
- VS Codeの推奨拡張は `.vscode/extensions.json` で管理する。
- VS Code拡張のバージョンは固定しない。更新を停止する場合は、各ユーザーのアプリケーション設定で行う。
- プロジェクト共通のVS Code設定は `.vscode/settings.json` で管理する。
- DockerでDBなど永続化すべきデータは名前付きボリュームで管理し、ホストOS固有の保存パスを設定に書かない。
- DockerのDBイメージはタグを固定し、`latest`相当の無指定タグに依存しない。
- 開発用ソースコードは、変更を即時反映するため必要に応じてバインドマウントする。
- 開発用コンテナは `backend/launch_container.sh start` で起動し、`stop` で停止する。
- DBスキーマの変更後は、Alembicでmigrationを適用する。

## Commit messages

- コミットメッセージはConventional Commits形式（`type: summary`）で記述する。
- Agent定義やSkill定義に関係しないMarkdownファイルの変更は `docs:` として扱う。
- Agent定義やSkill定義の変更は、内容に応じた専用のtypeまたは `chore:` を使う。

## Validation and handoff

- 変更後は、実行可能な範囲でテスト、静的検証、設定ファイルの構文検証を行う。
- 確認手順は実行するコマンドだけを記載せず、期待される実行結果や確認すべき状態も併記する。コマンドだけでは結果の検証につながらないためである。
- 未検証の事項や環境依存の事項は、最終報告に明記する。
