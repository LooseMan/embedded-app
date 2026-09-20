# Frontend

TypeScript + Next.js で作成したファイル管理GUIです。

## 起動

```sh
npm install
npm run dev
```

`http://localhost:3000` を開くと、ファイル一覧を確認できます。

## 画面の機能

- ファイル一覧のカード表示・リスト表示、名前検索、カテゴリフィルタ
- All files / Recent / Favorites / Trash のナビゲーション
- ファイル詳細パネルとダウンロード・ゴミ箱操作の導線
- アップロードモーダル、ストレージ使用状況、レスポンシブレイアウト

ファイル一覧は起動時に `GET /files`、カテゴリ名は `GET /file-categories` から取得します。開発時はNext.jsの同一オリジン `/api/*` rewrite経由でFastAPIへ転送するため、ブラウザのCORS設定に依存しません。APIの接続先を直接変更する場合は `NEXT_PUBLIC_API_BASE_URL` を指定できます。未設定時の転送先は `http://localhost:8000` です。
