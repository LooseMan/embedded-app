# embedded-app

## 構成

- `backend/`: FastAPI、SQLAlchemy、Alembic によるバックエンド
- `frontend/`: TypeScript + Next.js で実装予定のフロントエンド
- `docs/`: 設計資料と開発マニュアル

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
