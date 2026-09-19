pip-compile

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

## 構成

責務ごとに HTTP、業務処理、DB 永続化を分離しています。

```text
app/
├── api/                    # FastAPI の router と API 入出力
│   ├── routes.py
│   └── schemas.py
├── services/               # ユースケース・業務処理
│   └── calculation.py
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

docker run --name my-postgres -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dbname -d postgres

docker rm -f my-postgres

embedded-dev-automation/web/back/app

fastapi dev

| クラス                  | 継承元         | 用途                 |
| -------------------- | ----------- | ------------------ |
| **Pydantic Model**   | `BaseModel` | APIの入力・出力（JSON）    |
| **SQLAlchemy Model** | `Base`      | データベースのテーブル定義（ORM） |
