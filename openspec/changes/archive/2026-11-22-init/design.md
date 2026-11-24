# 設計書: 売上管理 (sales-management) 初期MVP

## Context

`reference/system-integration/usdm/sales_management/sheet01/SalesManagement_R01/` の要求仕様に基づき、売上レコードの受信登録（I-4）と期間別・チャネル別集計を提供する FastAPI マイクロサービスを構築する。

### USDM 要求トレーサビリティ

| USDM 要求/仕様ID | 内容 | 対応モジュール / エンドポイント |
| --- | --- | --- |
| `SalesManagement_R01` | 飲食店の日次・月次・年次売上を正確に集計・確認できること | `sales_management` 全体 |
| `SalesManagement_R01.DM01-01` | `POST /sales/records` で売上レコード（注文ID・チャネル・金額・計上日時）を登録できる（I-4） | `main.py` (`POST /sales/records`), `store.py`, `models.py` |
| `SalesManagement_R01.DM01-02` | `GET /sales/summary/daily`, `monthly`, `yearly` で期間別集計を取得できる | `main.py` (`/sales/summary/*`), `store.py` |
| `SalesManagement_R01.DM01-03` | 集計結果に総売上金額・注文件数・チャネル別内訳（`dine_in` / `takeout`）を含める | `models.py` (`SalesSummary`), `store.py` |

## Goals / Non-Goals

### Goals
- FastAPI + Pydantic v2 による型安全な API 実装
- インメモリストアによる高速・シンプルな MVP 実装（テストごとにリセット可能）
- 同一 `order_id` の重複登録を HTTP 409 Conflict で拒否する冪等性・整合性保護
- `recorded_at`（ISO8601）の日付プレフィックスに基づく日次（`YYYY-MM-DD`）・月次（`YYYY-MM`）・年次（`YYYY`）集計

### Non-Goals
- 永続化データベース（PostgreSQL / SQLite 等）の導入（MVP 後続フェーズで対応）
- 認証・認可および他サービスへの非同期イベント発行

## Decisions

1. **データモデル (`models.py`)**:
   - `Channel = Literal["dine_in", "takeout"]`
   - `SalesRecordCreate`: `order_id: str`, `payment_id: str`, `channel: Channel`, `amount: int = Field(ge=0)`, `recorded_at: datetime`（ISO8601 文字列を受理・検証）
   - `SalesRecord`: `id: str`, `order_id: str`, `payment_id: str`, `channel: Channel`, `amount: int`, `recorded_at: str`
   - `SalesSummary`: `period: str`, `total_amount: int`, `order_count: int`, `by_channel: dict[str, int]`（`{"dine_in": int, "takeout": int}`）
   - `HealthResponse`: `status: str`, `service: str`

2. **ストア設計 (`store.py`)**:
   - `SalesStore` クラスで `dict[str, SalesRecord]`（キー: `order_id`）を保持し、O(1) で重複チェックを行う。
   - 重複時はカスタム例外 `DuplicateOrderError` を送出し、`main.py` で HTTP 409 へ変換する。
   - 期間フィルタは ISO8601 日時（`YYYY-MM-DDTHH:MM:SS...`）の先頭文字列一致（`YYYY-MM-DD`, `YYYY-MM`, `YYYY`）で集計する。

3. **API 設計 (`main.py`)**:
   - `create_app() -> FastAPI` ファクトリ関数とモジュールレベル `app = create_app()` を提供。
   - `GET /health` -> `{"status": "ok", "service": "sales-management"}`
   - `POST /sales/records` (201) -> `SalesRecord`（重複時 409）
   - `GET /sales/summary/daily?date=YYYY-MM-DD` -> `SalesSummary`
   - `GET /sales/summary/monthly?month=YYYY-MM` -> `SalesSummary`
   - `GET /sales/summary/yearly?year=YYYY` -> `SalesSummary`
   - クエリパラメータの形式検証（正規表現パターン）を行い、不正形式には HTTP 422 を返す。
