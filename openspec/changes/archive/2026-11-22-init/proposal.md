# 変更提案: 売上管理 (sales-management) 初期MVP実装

## Why

飲食店向け支援システム（MachinakaRestaurantSupportTools）において、会計/注文管理から連携される売上レコード（I-4）を受信・蓄積し、日次・月次・年次およびチャネル別の売上集計を取得できる最小構成（MVP）のバックエンドAPIを提供するため。

## What Changes

- `sales-management` の Python / FastAPI プロジェクト基盤（`pyproject.toml`）を構築する
- 売上レコード登録 API（`POST /sales/records`、同一 `order_id` 重複時は HTTP 409）を実装する
- 日次・月次・年次売上集計 API（`GET /sales/summary/daily`, `monthly`, `yearly`）を実装する
- ヘルスチェック API（`GET /health`）およびチャネル別集計内訳（`dine_in` / `takeout`）を実装する
- `pytest` による単体試験を追加し、全テストのパスを確認する

## Capabilities

### New Capabilities

- `sales-reporting`: 売上レコードの受信登録（重複排除）および日次・月次・年次・チャネル別の売上集計機能

### Modified Capabilities

なし（新規構築）

## Impact

- 新規追加: `pyproject.toml`, `src/sales_management/`, `tests/test_sales.py`
- `reference/system-integration/`（読み取り専用サブモジュール）への変更はなし
