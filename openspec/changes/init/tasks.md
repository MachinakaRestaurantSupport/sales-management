# タスクリスト: 売上管理 (sales-management) 初期MVP

## 1. プロジェクト基盤

- [x] 1.1 Python プロジェクト基盤 (`pyproject.toml`) を作成する

## 2. アプリケーション実装

- [x] 2.1 Pydantic データモデル (`src/sales_management/__init__.py`, `models.py`) を実装する [SalesManagement_R01.DM01-01, SalesManagement_R01.DM01-03]
- [x] 2.2 インメモリ売上記録ストアと期間別集計ロジック (`src/sales_management/store.py`) を実装する [SalesManagement_R01.DM01-01, SalesManagement_R01.DM01-02, SalesManagement_R01.DM01-03]
- [x] 2.3 FastAPI アプリケーションとエンドポイント (`src/sales_management/main.py`) を実装する [SalesManagement_R01.DM01-01, SalesManagement_R01.DM01-02, SalesManagement_R01.DM01-03]

## 3. 検証・単体試験

- [x] 3.1 単体試験 (`tests/test_sales.py`) を作成し、`pytest` で全ケースがパスすることを確認する [SalesManagement_R01.DM01-01, SalesManagement_R01.DM01-02, SalesManagement_R01.DM01-03]
