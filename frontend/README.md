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

現在はバックエンド未起動でも画面確認できるよう、デモデータを表示しています。API接続を追加する場合は `app/page.tsx` の `files` データを `/files` と `/file-categories` の取得処理に置き換えてください。
