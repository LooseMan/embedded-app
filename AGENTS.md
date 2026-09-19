# Agent instructions

このファイルは、`embedded-app` リポジトリで作業するエージェント向けの指示です。
ユーザーの依頼と競合する場合は、ユーザーの依頼を優先してください。

## Repository map

- `backend/`: FastAPI、SQLAlchemy、Alembic
- `frontend/`: TypeScript、Next.js
- `docs/`: 設計資料、開発マニュアル
- `tests/`: テストとテスト手順

## Change rules

- 作業前に対象ファイルと関連実装を確認する。
- 既存の未コミット変更を上書き・破棄しない。
- 依頼範囲外の変更を追加しない。
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

- Python依存関係は `backend/requirements.in` を編集元、`backend/requirements.txt` を固定結果として扱う。
- VS Codeの推奨拡張は `.vscode/extensions.json` で管理する。
- VS Code拡張のバージョンは固定しない。更新を停止する場合は、各ユーザーのアプリケーション設定で行う。
- プロジェクト共通のVS Code設定は `.vscode/settings.json` で管理する。

## Validation and handoff

- 変更後は、実行可能な範囲でテスト、静的検証、設定ファイルの構文検証を行う。
- 未検証の事項や環境依存の事項は、最終報告に明記する。
